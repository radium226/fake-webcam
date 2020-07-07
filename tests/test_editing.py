#!/usr/bin/env python

from fakewebcam import editing
from fakewebcam import video
from fakewebcam.common import Size

from pathlib import Path


def test_loop():
    video.read_file(Path("tests/bmth.webm")).through(
        editing.resize(Size(800, 600)),
        editing.loop(count=2)
    ).to(video.play()).run()