#!/usr/bin/env python

from subprocess import Popen, PIPE

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
        frame_bytes = frame.tobytes()
        self._ffmpeg_process.stdin.write(frame_bytes)

    def __exit__(self, type, value, traceback):
        self._ffmpeg_process.kill()
        self._ffmpeg_process.wait()