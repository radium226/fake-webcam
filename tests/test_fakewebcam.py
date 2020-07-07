#!/usr/bin/env python

from fakewebcam.fakewebcam import FakeWebcam
from fakewebcam.editor import Editor
from pathlib import Path
from time import sleep

def test_show_bouncing_image_with_fake_webcam():
    fake_webcam = FakeWebcam(Path("/dev/video0"), dry_run=True)
    fake_webcam.start()
    sleep(5)
    fake_webcam.show_bouncing_image(Path("tests/open-source.png", frame_rate=fake_webcam.frame_rate))
    sleep(5)
    fake_webcam.stop()

def test_fake_webcam():
    fake_webcam = FakeWebcam(Path("/dev/video0"), dry_run=True)
    fake_webcam.start()
    fake_webcam.show_loop(duration=2)
    sleep(10)
    fake_webcam.show_default()
    sleep(10)
    fake_webcam.stop()

    
