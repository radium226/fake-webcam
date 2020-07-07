#!/usr/bin/env python

from ..process import stdout

import rx.operators as op

import numpy as np

from .recording import Recording

import cv2 as cv

from ..video import Video, probe

class Camera():

    def __init__(self, device_path, frame_size=None):
        self._device_path = device_path
        self._probe = probe(str(device_path))
        self._frame_size = frame_size
        
        self._video = None
        self._disposable = None

    @property
    def video(self):
        return self._video

    def record(self, file_path):
        recording = Recording(self, file_path)
        recording.start()
        return recording
            

    @property
    def frame_rate(self):
        return self._probe.frame_rate

    @property
    def frame_size(self):
        return self._frame_size or self._probe.size

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
            "-video_size", f"{self.frame_size.width}x{self.frame_size.height}",
            "-i", str(self.device_path), 
            "-c:v", "rawvideo", 
            "-an", 
            "-f", "image2pipe",
            "-s", f"{self.frame_size.width}x{self.frame_size.height}",
            "-pix_fmt", "bgr24",
            "-"
        ]

        frames = stdout(command, buffer_size=self.frame_size.width * self.frame_size.height * 3).pipe(
            op.map(lambda frame_bytes: np.frombuffer(frame_bytes, np.uint8).reshape((self.frame_size.height, self.frame_size.width, 3))),
            op.map(lambda frame: cv.cvtColor(frame, cv.COLOR_BGR2BGRA)),
            op.publish()
        )
        self._disposable = frames.connect()
        self._video = Video(frames, self.frame_size, self.frame_rate)

    def stop(self):
        self._disposable.dispose()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()


