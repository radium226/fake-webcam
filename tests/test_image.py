#!/usr/bin/env python

from fakewebcam.video import play
from fakewebcam.editing import take
from fakewebcam.image import solid, read_file

from pathlib import Path


BLUE = (255, 0, 0)

def test_solid():
    solid(BLUE).through(
        take(1)
    ).to(play()).run()


def test_read_file():
    read_file(Path("tests/open-source.png")).through(take(1)).to(play()).run()