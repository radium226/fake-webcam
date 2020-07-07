#!/usr/bin/env python

from fakewebcam.common import Size
from fakewebcam.fakecamera import FakeCamera
from fakewebcam.video import read_file
from fakewebcam.editing import resize

from pathlib import Path

def test_fake_camera():
    fake_camera = FakeCamera()
    fake_camera.start()

    read_file(Path("tests/bmth.webm")).through(resize(Size(800, 600))).to(fake_camera.video_sink).run()

    fake_camera.stop()