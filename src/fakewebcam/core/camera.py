#!/usr/bin/env python

from .process import stdout

import rx.operators as op

import numpy as np

from .recording import Recording
from .probe import probe


class Camera():

    def __init__(self, device_path, size=None):
        self._device_path = device_path
        self._probe = probe(str(device_path))
        self._size = size
        
        self._frames = None
        self._disposable = None

    @property
    def frames(self):
        return self._frames

    def record(self, file_path):
        print("[Camera] Starting to record... ")
        recording = Recording(self, file_path)
        recording.start()
        return recording

    @property
    def frame_rate(self):
        return self._probe.frame_rate

    @property
    def size(self):
        return self._size or self._probe.size

    @property
    def pixel_format(self):
        return self._probe.pixel_format

    @property
    def device_path(self):
        return self._device_path

    def start(self):
        command = [
            "ffmpeg",
            "-loglevel", "quiet", 
            "-f", "v4l2",
            "-input_format", self.pixel_format,
            "-framerate", str(self.frame_rate),
            "-video_size", f"{self.size.width}x{self.size.height}",
            "-i", str(self.device_path), 
            "-c:v", "rawvideo", 
            "-an", 
            "-f", "image2pipe",
            "-s", f"{self.size.width}x{self.size.height}",
            "-pix_fmt", "bgr24",
            "-"
        ]

        self._frames = stdout(command, buffer_size=self.size.width * self.size.height * 3).pipe(
            op.map(lambda frame_bytes: np.frombuffer(frame_bytes, np.uint8).reshape((self.size.height, self.size.width, 3))),
            op.publish()
        )
        self._disposable = self._frames.connect()

    def stop(self):
        self._disposable.dispose()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

