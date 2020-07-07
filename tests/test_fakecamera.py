#!/usr/bin/env python

from fakewebcam.core import FakeCamera
from fakewebcam import video
from fakewebcam import editing
from fakewebcam.common import Size

from pathlib import Path

from time import sleep


def test_fakecamera():
    default_video = video.read_file(Path("tests/ultra-vomit.mkv")).through(editing.resize(Size(800, 600)))
    fake_camera = FakeCamera(default_video)

    fake_camera.start(dry_run=True)
    sleep(3)
    fake_camera.stop()


def test_to_switch_video_with_fake_camera():
    default_video = video.read_file(Path("tests/bmth.webm")).through(editing.resize(Size(800, 600)))

    alt_video = video.read_file(Path("tests/ultra-vomit.mkv")).through(editing.take(1))

    fake_camera = FakeCamera(default_video)

    fake_camera.start(dry_run=True)
    sleep(2)
    fake_camera.switch_video(alt_video)
    sleep(2)
    fake_camera.stop()