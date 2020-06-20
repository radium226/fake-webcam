#!/usr/bin/env python

from .video import Video
from .process import stdin

import rx.operators as op

class Recording:

    def __init__(self, camera, file_path):
        self._camera = camera
        self._file_path = file_path

    @property
    def video(self):
        return Video(self._file_path)

    def start(self):
        print("RECORDIIIIING")
        self._disposable = self._camera.frames.pipe(
            op.map(lambda frame: frame.tobytes()), 
            stdin([
                "ffmpeg", 
                "-y",
                #"-loglevel", "quiet",
                "-f", "rawvideo",
                "-video_size", f"{self._camera.size.width}x{self._camera.size.height}",
                "-r", str(self._camera.frame_rate),
                "-pixel_format", "bgr24",
                "-i", "-", 
                "-an",
                "-codec:v", "libx264",
                "-f", "mp4", 
                str(self._file_path)
            ])
        ).subscribe()


    def stop(self):
        self._disposable.dispose()