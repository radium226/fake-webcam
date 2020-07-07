#!/usr/bin/env python

from fakewebcam.camera import Camera
from fakewebcam.video import play

from pathlib import Path
from time import sleep


def test_camera():
    camera = Camera(device_path=Path("/dev/video0"))
    camera.start()
    disposable = camera.video.to(play()).subscribe()
    sleep(5)
    disposable.dispose()
    camera.stop()

def test_recording_with_camera():
    camera = Camera(device_path=Path("/dev/video0"))
    camera.start()
    
    recording = camera.record(Path("tests/recording.mp4"))
    sleep(5)
    recording.stop()

    recording.video.to(play()).run()

    camera.stop()

