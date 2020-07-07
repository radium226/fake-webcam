#!/usr/bin/env python

from fakewebcam import video
from fakewebcam import image
from fakewebcam.editing import resize, overlay
from fakewebcam.common import Size
from fakewebcam.animation import bounce
from pathlib import Path

def test_bounce_with_video():
    video.read_file(Path("tests/bmth.webm")).through(
        resize(Size(400, 300)), 
        bounce(),
    ).to(video.play()).run()


def test_bounce_with_image():
    image.read_file(Path("tests/open-source.png")).through(bounce()).to(video.play()).run()


def test_overlay_with_boucing_image():
    overlay_video = image.read_file(Path("tests/open-source.png")).through(resize(Size(400, 300)), bounce())

    video.read_file(Path("tests/bmth.webm")).through(
        resize(Size(400, 300)), 
        overlay(overlay_video),
    ).to(video.play()).run()