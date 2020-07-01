#!/usr/bin/env python

from .process import stdin
import rx.operators as op

import cv2 as cv

def player(size, frame_rate):
    def subscribe(source):
        print("We are here! ")
        return source.pipe(
            #op.map(lambda frame: cv.cvtColor(frame, cv.COLOR_BGRA2BGR)),
            op.map(lambda frame: frame.tobytes()), 
            stdin([
                "ffplay", 
                "-loglevel", "quiet",
                "-autoexit", 
                "-f", "rawvideo",
                "-video_size", f"{size.width}x{size.height}",
                "-pixel_format", "bgr24",
                "-framerate", str(frame_rate), 
                "-i", "-"
            ])
        )
    return subscribe
