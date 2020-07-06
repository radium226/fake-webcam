#!/usr/bin/env python

from .videosink import VideoSink
from ..core.process import stdin
from ..source.videosource import VideoSource

from rx import operators as op


class PlayVideoSink(VideoSink):

    def __init__(self):
        pass


    def drain(self, video_source):
        return video_source.frames.pipe(
            op.map(lambda frame: frame.tobytes()), 
            stdin([
                "ffplay", 
                "-loglevel", "quiet",
                "-autoexit", 
                "-f", "rawvideo",
                "-video_size", f"{video_source.frame_size.width}x{video_source.frame_size.height}",
                "-pixel_format", "bgr24",
                "-framerate", str(video_source.frame_rate), 
                "-i", "-"
            ])
        )


def play():
    return PlayVideoSink()