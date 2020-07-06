#!/usr/bin/env python

from fakewebcam.effect import OverlayEffect
from fakewebcam.core.video import Video
from fakewebcam.core.player import player

from pathlib import Path

#from .runner import runner


UV_VIDEO_FILE_PATH = Path("tests/ultra-vomit.mkv")
BMTH_VIDEO_FILE_PATH = Path("tests/bmth.webm")


def test_video():
    return 
    o = Video(BMTH_VIDEO_FILE_PATH)
    e = OverlayEffect(o)
    
    v = Video(UV_VIDEO_FILE_PATH)

    p = player(v.size, v.frame_rate)
    v.frames.pipe(
        e.operator(v.size, v.frame_rate), 
        p,
    ).run()


