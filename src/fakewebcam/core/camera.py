#!/usr/bin/env python

from .process import stdout

import rx.operators as op

import numpy as np


class Camera():

    def __init__(self, device_path, size=None, format=None, frame_rate=None):
        self._device_path = device_path
        self._size = size
        self._format = format
        self._frame_rate = frame_rate

        self._frames = None
        self._disposable = None

    @property
    def frames(self):
        return self._frames

    @property
    def size(self):
        return self._size

    def start(self):
        device_path = self._device_path
        size = self._size
        format = self._format
        frame_rate = self._frame_rate

        command = [
            "ffmpeg",
            "-loglevel", "quiet", 
            "-f", "v4l2",
            "-input_format", format,
            "-framerate", str(frame_rate),
            "-video_size", f"{size.width}x{size.height}",
            "-i", str(device_path), 
            "-c:v", "rawvideo", 
            "-an", 
            "-f", "image2pipe",
            "-s", f"{size.width}x{size.height}",
            "-pix_fmt", "bgr24",
            "-"
        ]

        self._frames = stdout(command, buffer_size=size.width * size.height * 3).pipe(
            #op.map(lambda frame_bytes: np.frombuffer(frame_bytes, np.uint8).reshape((self.size.height, self.size.width, 3))),
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


