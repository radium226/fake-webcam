#!/usr/bin/env python

from .videosink import VideoSink
from ..core.process import stdin

import rx.operators as ops
import cv2


class PlayVideoSink(VideoSink):
    
    def __init__(self):
        pass

    def drain(self, video):
        return video.frames.pipe(
            ops.map(lambda bgra_frame: cv2.cvtColor(bgra_frame, cv2.COLOR_BGRA2BGR)),
            ops.map(lambda frame: frame.tobytes()), 
            stdin([
                "ffplay", 
                "-loglevel", "quiet",
                "-autoexit", 
                "-f", "rawvideo",
                "-video_size", f"{video.frame_size.width}x{video.frame_size.height}",
                "-pixel_format", "bgr24",
                "-framerate", str(video.frame_rate), 
                "-i", "-"
            ])
        )


def play():
    return PlayVideoSink()