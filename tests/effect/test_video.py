#!/usr/bin/env python

from fakewebcam.common import Size
from fakewebcam.source import *
from fakewebcam.sink import *
from pathlib import Path

def test_video():
    size = Size(100, 100)
    print(size)

    video_source = ReadFileVideoSource(Path("tests/bmth.webm"))

    video_source \
        .resize(size).play()
