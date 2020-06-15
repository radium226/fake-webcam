#!/usr/bin/env python

from pyudev import Context

from queue import Queue
from collections import namedtuple
from threading import Thread
from subprocess import Popen, PIPE

from functools import partial
from time import sleep



# ffmpeg -f v4l2 -input_format yuyv -framerate 25 -video_size 640x480 -i /dev/video0 output.mkv
# v4l2-ctl --list-formats-ext

Size = namedtuple("Size", ["width", "height"])
Config = namedtuple("Config", ["size", "frame_rate", "format"])

#with Camera.sysfs_folder("/dev/video0").recorder() as recorder, Player() as player:
#    while True:
#        frame = recorder.record_frame()
#        player.play_frame(frame)


#def modprobe(module_name, **kwargs):
#    pass

#class Format(Enum):

#    YUYV = 1

class Recorder:

    def __init__(self, device_path, size, format, frame_rate):
        self._device_path = device_path
        self._format = format
        self._size = size
        self._frame_rate = frame_rate

        self._frame_queue = None
        self._enqueue_thread = None
        self._ffmpeg_process = None


    def _ffmpeg_command(self):
        return [
            "ffmpeg",
            #"-loglevel", "quiet", 
            "-f", "v4l2",
            "-input_format", self._format,
            "-framerate", str(self._frame_rate),
            "-video_size", f"{self._size.width}x{self._size.height}",
            "-i", str(self._device_path), 
            "-c:v", "rawvideo", 
            "-an", 
            "-f", "image2pipe",
            "-s", f"{self._size.width}x{self._size.height}",
            "-pix_fmt", "bgr24",
            "-"
        ]

    def __enter__(self):
        ffmpeg_command = self._ffmpeg_command()
        print(f"ffmpeg_command={' '.join(ffmpeg_command)}")
        self._frame_queue = Queue(maxsize=1)
        self._ffmpeg_process = Popen(ffmpeg_command, stdout=PIPE)
            
        def enqueue_thread_target():
            buffer_size = self._size.width * self._size.height * 3
            print(f"buffer_size={buffer_size}")
            for frame_bytes in iter(partial(self._ffmpeg_process.stdout.read, buffer_size), b""):
                #print("Enqueuing frame! ")
                self._frame_queue.put(frame_bytes)

        self._enqueue_thread = Thread(target=enqueue_thread_target)
        self._enqueue_thread.start()
        return self

    def __exit__(self, type, value, traceback):
        self._ffmpeg_process.kill()
        self._enqueue_thread.join() 

    
    def record_frame(self):
        return self._frame_queue.get()


class Player():

    def __init__(self, size):
        self._size = size
        self._ffplay_process = None

    def _ffplay_command(self):
        return [
            "ffplay", 
            #"-loglevel", "quiet",
            "-f", "rawvideo",
            "-video_size", f"{self._size.width}x{self._size.height}",
            "-pixel_format", "bgr24",
            "-i", "-"
        ]

    def __enter__(self):
        ffplay_command = self._ffplay_command()
        print(f"ffplay_command={' '.join(ffplay_command)}")
        self._ffplay_process = Popen(ffplay_command, stdin=PIPE)
        return self

    def play_frame(self, frame):
        self._ffplay_process.stdin.write(frame)

    def __exit__(self, type, value, traceback):
        self._ffplay_process.kill()
        self._ffplay_process.wait()


class Camera:

    def __init__(self, device_path):
        self._device_path = device_path

    
    def list_formats(self):
        pass

    def recorder(self, size, format, frame_rate):
        return Recorder(self._device_path, size, format, frame_rate)

class FakeCameraPlayer:

    def __init__(self, fake_camera, size):
        self._size = size
        self._fake_camera = fake_camera
        self._ffmpeg_process = None

    @property
    def fake_camera(self):
        return self._fake_camera

    def _ffmpeg_command(self):
        return [
            "ffmpeg", 
            "-f", "rawvideo",
            "-video_size", f"{self._size.width}x{self._size.height}",
            "-pixel_format", "bgr24",
            "-i", "-", 
            "-vf", f"scale=iw*min({self.fake_camera.size.width}/iw\,{self.fake_camera.size.height}/ih):ih*min({self.fake_camera.size.width}/iw\,{self.fake_camera.size.height}/ih),pad={self.fake_camera.size.width}:{self.fake_camera.size.height}:({self.fake_camera.size.width}-iw)/2:({self.fake_camera.size.height}-ih)/2", 
            "-vcodec", "rawvideo", 
            "-pix_fmt", "yuv420p", 
            "-f", "v4l2", 
            str(self.fake_camera.device_path)
        ]

    def __enter__(self):
        ffmpeg_command = self._ffmpeg_command()
        print(f"ffmpeg_command={' '.join(ffmpeg_command)}")
        self._ffmpeg_process = Popen(ffmpeg_command, stdin=PIPE)
        return self

    def play_frame(self, frame):
        self._ffmpeg_process.stdin.write(frame)

    def __exit__(self, type, value, traceback):
        self._ffmpeg_process.kill()
        self._ffmpeg_process.wait()

class FakeCamera:

    def __init__(self, device_path, size):
        self._device_path = device_path
        self._size = size

    @property
    def device_path(self):
        return self._device_path

    @property
    def size(self):
        return self._size

    @property
    def size(self):
        return self._size

    def player(self, size=None):
        return FakeCameraPlayer(self, size or self.size)



def run():
    size = Size(160, 120)

    camera = Camera("/dev/video0")
    fake_camera = FakeCamera("/dev/video2", size=Size(800, 600))

    with camera.recorder(size=size, format="yuyv422", frame_rate=30) as recorder, fake_camera.player() as player:
        while True:
            frame = recorder.record_frame()
            player.play_frame(frame)


    #modprobe("v4l")
    #context = Context()
    #for device in context.list_devices(subsystem="video4linux", ID_V4L_PRODUCT="Fake"):
    #    print(device)