#!/usr/bin/env python

from ..spi import Sink
from ...core.process import stdin

from rx import operators as op

class FileWriter(Sink):
    
    def __init__(self, file_path):
        self._file_path = file_path

    def drain(self, source):
        return source.frames.pipe(
            op.map(lambda frame: frame.tobytes()), 
            stdin([
                "ffmpeg", 
                "-y",
                #"-loglevel", "quiet",
                "-f", "rawvideo",
                "-video_size", f"{source.frame_size.width}x{source.frame_size.height}",
                "-r", str(source.frame_rate),
                "-pixel_format", "bgr24",
                "-i", "-", 
                "-an",
                "-codec:v", "libx264",
                "-f", "mp4", 
                str(self._file_path)
            ])
        )



def write_file(file_path):
    return FileWriter(file_path)

