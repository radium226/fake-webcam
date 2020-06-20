#!/usr/bin/env python

from .process import stdout
from MediaInfo import MediaInfo
from .size import Size

import numpy as np
import rx.operators as op
import cv2

from .probe import probe


class Video:

    def __init__(self, file_path, loop=False, reverse=False, _probe=None):
        self._file_path = file_path
        self._loop = loop
        self._reverse = reverse
        self._probe = _probe or probe(str(file_path))

    @property
    def size(self):
        return self._probe.size

    @property
    def reverse(self):
        return Video(self._file_path, loop=self._loop, reverse=not self._reverse, _probe=self._probe)

    @property
    def loop(self):
        return Video(self._file_path, loop=True, reverse=self._reverse, _probe=self._probe)

    @property
    def unloop(self):
        return Video(self._file_path, loop=False, reverse=self._reverse, _probe=self._probe)

    @property
    def frames(self):
        command = [
            "ffmpeg",
            "-loglevel", "quiet", 
            "-i", str(self._file_path)
        ] + (["-vf", "reverse"] if self._reverse else []) + [
            "-c:v", "rawvideo", 
            "-an", 
            "-f", "image2pipe",
            "-s", f"{self.size.width}x{self.size.height}",
            "-pix_fmt", "bgr24",
            "-"
        ]
        
        observable = stdout(command, buffer_size=self.size.width * self.size.height * 3).pipe(
            op.map(lambda frame_bytes: np.frombuffer(frame_bytes, np.uint8).reshape((self.size.height, self.size.width, 3))), 
            #op.map(lambda frame: cv2.circle(frame, (100, 100), 10, (255, 0, 0), 2))
        )
        if self._loop:
            return observable.pipe(op.concat(self.unloop.reverse.frames)).pipe(op.repeat())
        else:
            return observable
    