#!/usr/bin/env python

#from .video import Video
from ..core.process import stdin

from ..video import read_file, write_file

import rx.operators as op

class Recording:

    def __init__(self, camera, file_path):
        self._camera = camera
        self._file_path = file_path

    @property
    def file_path(self):
        return self._file_path

    @property
    def video(self):
        return read_file(self._file_path)

    def start(self):
        self._disposable = self._camera.video.to(write_file(self.file_path)).subscribe()


    def stop(self):
        self._disposable.dispose()