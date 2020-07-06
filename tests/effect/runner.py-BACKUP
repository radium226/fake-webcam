#!/usr/bin/env python

from fakewebcam.core import Video
from fakewebcam.core.player import player

def runner(v, e):
    p = player(v.size, v.frame_rate)
    v.frames.pipe(
        e.operator(v.size, v.frame_rate), 
        p,
    ).run()