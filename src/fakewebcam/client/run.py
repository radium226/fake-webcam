#!/usr/bin/env python

from pyudev import Context

from queue import Queue, Empty
from collections import namedtuple
from threading import Thread, Lock
from subprocess import Popen, PIPE

from functools import partial
from time import sleep

import cv2
import numpy as np

Size = namedtuple("Size", ["width", "height"])
Config = namedtuple("Config", ["size", "frame_rate", "format"])

from .camera import Camera
from .fakecamera import FakeCamera
from .player import Player

from pathlib import Path

from enum import Enum
from MediaInfo import MediaInfo

FFMPEG_LOG_LEVEL = "quiet"

LAST_FRAME = None

            

class SourceKind(Enum):

    CAMERA = 1
    FILE = 2


class FakeWebcam:

    def __init__(self, fallback_source, sink):
        self._fallback_source = fallback_source
        self._source = fallback_source
        self._sink = sink
        self._started = True

        self._lock = Lock()


    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, new_source):
        print("[FakeWebcam] Acquiring lock in source switch... ")
        self._lock.acquire()
        print("[FakeWebcam] Lock acquired in source switch! ")
        print("[FakeWebcam] Switching source... ")
        old_source = self._source
        new_source.connect()
        self._source = new_source
        if old_source:
            old_source.disconnect()
        print("[FakeWebcam] Source switched! ")
        print("[FakeWebcam] Releasing lock in source switch... ")
        self._lock.release()
        print("[FakeWebcam] Lock released in source switch! ")

    def start(self):
        def loop_thread_target():
            while True:
                print("[FakeWebcam] Acquiring lock in loop... ")
                self._lock.acquire()
                #if self._started:
                print("[FakeWebcam] Lock acquired in loop... ")
                print("[FakeWecam] Reading frame... ")
                source = self._source
                frame = source.read_frame()
                if frame is LAST_FRAME:
                    print("[FakeWebcam] Last frame read! ")
                    if self._started:
                        self._lock.release()
                        self.source = self._fallback_source
                    else:    
                        self._lock.release()
                        break
                else:
                    if self._started:
                        print("[FakeWebcam] Frame read! ")
                        self._sink.write_frame(frame)
                    print("[FakeWebcam] Releasing lock in loop... ")
                    self._lock.release()
                    print("[FakeWebcam] Lock released in loop... ")
        self._loop_thread = Thread(target=loop_thread_target)
        
        if self._source:
            self._source.connect()
        
        if self._sink:
            self._sink.connect()
        
        self._loop_thread.start()

    def stop(self):
        self._lock.acquire()
        self._started = False        
        if self._sink:
            print("[FakeWebcam] Disconnecting sink... ")
            self._sink.disconnect()
            print("[FakeWebcam] Sink disconnected! ")
        
        if self._source:
            print("[FakeWebcam] Disconnecting source... ")
            self._source.disconnect()
            print("[FakeWebcam] Source disconnected! ")
        self._lock.release()
        
        self._loop_thread.join()
        self.wait()
        


    def wait(self):
        self._loop_thread.join()


class PlayerSink:

    def __init__(self, size):
        self._size = size
        self._ffplay_process = None

    def connect(self):
        ffplay_command = [
            "ffplay", 
            "-loglevel", FFMPEG_LOG_LEVEL,
            "-autoexit", 
            "-f", "rawvideo",
            "-video_size", f"{self._size.width}x{self._size.height}",
            "-pixel_format", "bgr24",
            "-i", "-"
        ]
        self._ffplay_process = Popen(ffplay_command, stdin=PIPE)


    def disconnect(self):
        self._ffplay_process.stdin.close()
        self._ffplay_process.wait()
        self._ffplay_process = None

    def write_frame(self, frame):
        self._ffplay_process.stdin.write(frame.tobytes())
        


class FileSource:

    def __init__(self, file_path, size, loop=False):
        self._file_path = file_path
        self._size = size
        self._loop = loop

        loop_command_options = []
        if self._loop:
            media_info = MediaInfo(filename=str(file_path)).getInfo()
            frame_rate = float(media_info.get("videoFrameRate"))
            duration = float(media_info.get("duration"))
            loop_command_options = ["-filter_complex", f"[0]reverse[r];[0][r]concat,loop=-1:{int(frame_rate * duration) * 2},setpts=N/{int(frame_rate)}/TB"] if self._loop else []

        command = [
            "ffmpeg",
            "-loglevel", FFMPEG_LOG_LEVEL, 
            "-i", str(self._file_path)
        ] + loop_command_options + [
            "-c:v", "rawvideo", 
            "-an", 
            "-f", "image2pipe",
            "-s", f"{self._size.width}x{self._size.height}",
            "-pix_fmt", "bgr24",
            "-"
        ]

        self._process_source = ProcessSource(command, size)

    def connect(self):
        print("[FileSource] Connecting...")
        self._process_source.connect()
        print("[FileSource] Connected! ")

    def read_frame(self):
        print("[FileSource] Reading frame.... ")
        frame = self._process_source.read_frame()
        print("[FileSource] Frame read! ")
        return frame

    def disconnect(self):
        print("[FileSource] Disconnecting! ")
        self._process_source.disconnect()
        print("[FileSource] Disconnected! ")


class ProcessSource:

    def __init__(self, command, size):
        self._command = command
        self._size = size

        self._process = None
        self._frame_queue = None
        self._put_frame_thread = None
        self._wait_process_thread = None

    def connect(self):
        self._frame_queue = Queue()

        print(f"command={self._command}")
        self._process = Popen(self._command, stdout=PIPE)

        def wait_process_thread_target():
            self._process.wait()
            self._frame_queue.put(LAST_FRAME)
        
        def put_frame_thread_target():
            buffer_size = self._size.width * self._size.height * 3
            #print(f"buffer_size={buffer_size}")
            for frame_bytes in iter(partial(self._process.stdout.read, buffer_size), b""):
                if frame_bytes is not None:
                    frame = np.frombuffer(frame_bytes, np.uint8).reshape((self._size.height, self._size.width, 3))
                    self._frame_queue.put(frame)

        self._put_frame_thread = Thread(target=put_frame_thread_target)
        self._wait_process_thread = Thread(target=wait_process_thread_target)
        self._wait_process_thread.start()
        self._put_frame_thread.start()

    def read_frame(self):
        #while True:
            #try:
            #    if self._frame_queue:
        frame = self._frame_queue.get()
        return frame
            #except Empty:
            #    print("[FakeWebcam] <Empty>")
            #    continue


    def disconnect(self):
        self._process.kill()
        self._process.wait()
        self._put_frame_thread.join()
        self._wait_process_thread.join()
        self._frame_queue.put(LAST_FRAME)

        self._process = None
        #self._frame_queue = None
        self._put_frame_thread = None

class CameraSource:

    def __init__(self, device_path, size, format, frame_rate):
        self._device_path = device_path
        self._size = size
        self._format = format
        self._frame_rate = frame_rate

        command = [
            "ffmpeg",
            "-loglevel", FFMPEG_LOG_LEVEL, 
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

        self._process_source = ProcessSource(command, size)

    def connect(self):
        print("[CameraSource] Connecting... ")
        self._process_source.connect()
        print("[CameraSource] Connected! ")

    def read_frame(self):
        print("[CameraSource] Reading frame...")
        frame = self._process_source.read_frame()
        print("[CameraSource] Frame read! ")
        return frame

    def disconnect(self):
        print("[CameraSource] Disconnecting...")
        self._process_source.disconnect()
        print("[CameraSource] Disconnected! ")

def run():
    size = Size(960, 544)

    #camera_source = CameraSource("/dev/video0", size=size, format="yuyv422", frame_rate=30)
    player_sink = PlayerSink(size=size)
    file_source = FileSource("output.mp4", size=size, loop=True)
    
    fake_webcam = FakeWebcam(file_source, player_sink)
    fake_webcam.start()

    def thread_target():
        #sleep(2)
        #print("Setting File Source... ")
        #fake_webcam.source = file_source
        #print("File Source Set! ")
        sleep(15)
        print("Stopping... ")
        fake_webcam.stop()
        print("Stopped! ")

    thread_target = Thread(target=thread_target)
    thread_target.start()

    fake_webcam.wait()


    #with camera.recorder(size=size, format="yuyv422", frame_rate=30) as camera_recorder, camera_recorder.record(Path("./record.avi")), Player(size) as player:
    #    while True:
    #        frame = camera_recorder.record_frame()
    #        #rotated_frame = cv2.rotate(frame, cv2.ROTATE_180)
    #        player.play_frame(frame)





# ffmpeg -f v4l2 -input_format yuyv -framerate 25 -video_size 640x480 -i /dev/video0 output.mkv
# v4l2-ctl --list-formats-ext





#with Camera.sysfs_folder("/dev/video0").recorder() as recorder, Player() as player:
#    while True:
#        frame = recorder.record_frame()
#        player.play_frame(frame)


#def modprobe(module_name, **kwargs):
#    pass

#class Format(Enum):

#    YUYV = 1



'''
class FakeWebcam:

    def __init__(self, camera, fake_camera):
        self._camera = camera
        self._fake_camera = fake_camera


    

    def start_recording(self):
        pass

    def stop_recording(self):
        pass



class FakeWebcamObject:

    def __init__(self, fake_webcam):
        self._fake_webcam = fake_webcam

    def StartRecording(self):
        self._fake_webcam.start_recording()

    def StopRecording(self):
        self._fake_webcam.stop_recording()

'''


    #modprobe("v4l")
    #context = Context()
    #for device in context.list_devices(subsystem="video4linux", ID_V4L_PRODUCT="Fake"):
    #    print(device)