#!/usr/bin/env python

from ..camera import Camera
from ..fakecamera import FakeCamera
from ..editing import loop, resize
from ..animation import bounce
from ..editor import Editor
from ..video import play
from ..image import read_file

from time import sleep
from tempfile import mkstemp
from threading import Thread
from pathlib import Path

from ..editing import overlay

class FakeWebcam:

    def __init__(self, device_path, dry_run=True):
        self._fake_camera = FakeCamera()
        self._camera = Camera(device_path)
        self._editor = None
        self._dry_run = dry_run

    def start(self):
        self._fake_camera.start()
        self._camera.start()
        
        self._editor = Editor(self._camera.video, play() if self._dry_run else self._fake_camera.video_sink)
        self._editor.start()

    @property
    def frame_size(self):
        return self._editor.frame_size

    @property
    def frame_rate(self):
        return self._editor.frame_rate

    def stop(self):
        self._editor.stop()

        self._camera.stop()
        self._fake_camera.stop()
        
    def show_loop(self, duration):
        def thread_target():
            _, file_path = mkstemp(suffix=".mp4", prefix="fake-webcam")
            recording = self._camera.record(Path(file_path))
            sleep(duration)
            recording.stop()
            self._editor.switch_video(recording.video.through(loop()))
        thread = Thread(target=thread_target)
        thread.start()

    def show_bouncing_image(self, image_file_path):
        self._editor.switch_editing(overlay(read_file(image_file_path).through(
            resize(self._editor.frame_size), 
            bounce(duration=1)
        )))

    def show_default(self):
        self._editor.switch_video(self._camera.video)
        
