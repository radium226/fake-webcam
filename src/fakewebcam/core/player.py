#!/usr/bin/env python

from .process import stdin

def player(size):
    return stdin([
        "ffplay", 
        "-loglevel", "quiet",
        "-f", "rawvideo",
        "-video_size", f"{size.width}x{size.height}",
        "-pixel_format", "bgr24",
        "-i", "-"
    ])
