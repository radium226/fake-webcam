#!/usr/bin/env python

from .process import stdin
import rx.operators as op

def player(size):
    def subscribe(source):
        return source.pipe(
            #op.map(lambda frame: frame.tobytes()), 
            stdin([
                "ffplay", 
                "-loglevel", "quiet",
                "-autoexit", 
                "-f", "rawvideo",
                "-video_size", f"{size.width}x{size.height}",
                "-pixel_format", "bgr24",
                "-i", "-"
            ])
        )
    return subscribe
