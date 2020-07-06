#!/usr/bin/env python

from .spi.source import Source
from .source.filereader import FileReader

class Video(Source):

    def __init__(self, frames, frame_size, frame_rate):
        self._frames = frames
        self._frame_size = frame_size
        self._frame_rate = frame_rate

    @property
    def frames(self):
        return self._frames

    @property
    def frame_size(self):
        return self._frame_size

    @property
    def frame_rate(self):
        return self._frame_rate

    @classmethod
    def read_file(cls, file_path):
        return FileReader(file_path)