#!/usr/bin/env python

#from fakewebcam.effect import ImageEffect
from fakewebcam.core import Video
from fakewebcam.core.player import player

from fakewebcam.effect import ImageOverlayEffect

from pathlib import Path


VIDEO_FILE_PATH = Path("tests/ultra-vomit.mkv")

IMAGE_FILE_PATH = Path("image.svg")

def test_image_effect():
    return 
    assert(VIDEO_FILE_PATH.exists())

    v = Video(VIDEO_FILE_PATH)
    p = player(v.size, v.frame_rate)

    e = ImageOverlayEffect(IMAGE_FILE_PATH)

    v.frames.pipe(
        e.operator(v.size, v.frame_rate), 
        p,
    ).run()