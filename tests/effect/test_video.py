#!/usr/bin/env python

from fakewebcam.common import Size
from fakewebcam.source import *
from fakewebcam.sink import *
from pathlib import Path

def test_video():
    size = Size(100, 100)
    print(size)

    bmth = VideoFile()
    uv = VideoFile()

    v = uv.through(
        resize_frames(Size(800, 600)), 
        gray(), 
        overlay(bmth.through(resize_frames(Size(200, 100))))
    )

    v.through(play())
