#!/usr/bin/env python

from ..spi import Sink
from ...core.process import stdin
import rx.operators as op

class Player(Sink):
    
    def __init__(self):
        pass

    def drain(self, source):
        return source.frames.pipe(
            op.map(lambda frame: frame.tobytes()), 
            stdin([
                "ffplay", 
                "-loglevel", "quiet",
                "-autoexit", 
                "-f", "rawvideo",
                "-video_size", f"{source.frame_size.width}x{source.frame_size.height}",
                "-pixel_format", "bgr24",
                "-framerate", str(source.frame_rate), 
                "-i", "-"
            ])
        )


def play():
    return Player()