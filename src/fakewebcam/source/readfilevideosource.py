#!/usr/bin/env python

from .videosource import VideoSource
from ..common import Size

# FIXME: It should be in another package
from ..core.probe import probe
from ..core.process import stdout

import rx
from rx import operators as op
import numpy as np


class ReadFileVideoSource(VideoSource):

    def __init__(self, file_path):
        self._file_path = file_path
        self._probe = probe(str(file_path))

    @property
    def frame_size(self):
        return self._probe.size

    @property
    def frames(self):
        command = [
            "ffmpeg",
            "-loglevel", "quiet", 
            "-i", str(self._file_path),
            "-c:v", "rawvideo", 
            "-an", 
            "-f", "image2pipe",
            "-s", f"{self.frame_size.width}x{self.frame_size.height}",
            "-pix_fmt", "bgr24",
            "-"
        ]
        
        return stdout(command, buffer_size=self.frame_size.width * self.frame_size.height * 3).pipe(
            op.map(lambda frame_bytes: np.frombuffer(frame_bytes, np.uint8).reshape((self.frame_size.height, self.frame_size.width, 3)))
        )

    @property
    def frame_rate(self):
        return self._probe.frame_rate