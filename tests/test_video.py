#!/usr/bin/env python

from fakewebcam.video import read_file, play, write_file
from fakewebcam.editing import gray, resize, overlay

from pathlib import Path
from fakewebcam.common import Size, Position

BMTH_VIDEO = read_file(Path("tests/bmth.webm"))
UV_VIDEO = read_file(Path("tests/ultra-vomit.mkv"))

def test_to_play_video():
    BMTH_VIDEO.to(play()).run()

def test_gray_effect():
    BMTH_VIDEO.through(
        gray()
    ).to(play()).run()

def test_resize_effect():
    BMTH_VIDEO.through(
        resize(Size(200, 100))
    ).to(play()).run()

def test_chained_effects():
    BMTH_VIDEO.through(
        resize(Size(200, 100)), 
        gray(),
    ).to(play()).run()

def test_to_write_video():
    BMTH_VIDEO.through(resize(Size(200, 100))).to(write_file(Path("tests/bmth.mp4"))).run()

def test_overlay():
    UV_VIDEO.through(
        resize(Size(800, 400)),
        overlay(BMTH_VIDEO.through(gray(), resize(Size(200, 100))), position=Position(20, 20))
    ).to(play()).run()
    