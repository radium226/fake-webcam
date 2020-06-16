#!/usr/bin/env python

from subprocess import Popen, PIPE

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
        frame_bytes = frame.tobytes()
        self._ffplay_process.stdin.write(frame_bytes)

    def __exit__(self, type, value, traceback):
        self._ffplay_process.kill()
        self._ffplay_process.wait()