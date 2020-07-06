#!/usr/bin/env python

from .videosink import VideoSink
from ..core.process import stdin
from ..source.videosource import VideoSource

from rx import operators as op


class PlayVideoSink(VideoSink):

    def __init__(self, frame_size, frame_rate):
        self._frame_rate = frame_rate
        self._frame_size = frame_size

    @property
    def frames(self):
        def subscribe(source_frames):
            return source_frames.pipe(
                op.map(lambda frame: frame.tobytes()), 
                stdin([
                    "ffplay", 
                    "-loglevel", "quiet",
                    "-autoexit", 
                    "-f", "rawvideo",
                    "-video_size", f"{self._frame_size.width}x{self._frame_size.height}",
                    "-pixel_format", "bgr24",
                    "-framerate", str(self._frame_rate), 
                    "-i", "-"
                ])
            )
        return subscribe


def play():
    def _play(video_source):
        video_source.frames.pipe(
            PlayVideoSink(video_source.frame_size, video_source.frame_rate).frames
        ).run()
    return _play