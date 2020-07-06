#!/usr/bin/env python

from ..core.process import stdin
from .videosink import VideoSink

from rx import operators as ops


class WriteFileVideoSink(VideoSink):
    
    def __init__(self, file_path):
        self._file_path = file_path

    def drain(self, video):
        return video.frames.pipe(
            ops.map(lambda frame: frame.tobytes()), 
            stdin([
                "ffmpeg", 
                "-y",
                #"-loglevel", "quiet",
                "-f", "rawvideo",
                "-video_size", f"{video.frame_size.width}x{video.frame_size.height}",
                "-r", str(video.frame_rate),
                "-pixel_format", "bgr24",
                "-i", "-", 
                "-an",
                "-codec:v", "libx264",
                "-f", "mp4", 
                str(self._file_path)
            ])
        )



def write_file(file_path):
    return WriteFileVideoSink(file_path)

