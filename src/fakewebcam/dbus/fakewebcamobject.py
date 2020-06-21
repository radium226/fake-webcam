#!/usr/bin/env python

from ..core import Camera, FakeCamera, Video

from dbus.service import Object, method

from time import sleep
from tempfile import mkstemp
from pathlib import Path
from threading import Thread


class FakeWebcamObject(Object):

    OBJECT_PATH = '/com/github/radium226/FakeWebcam'
    DBUS_INTERFACE = 'com.github.radium226.FakeWebcam'


    def __init__(self, bus, bus_name):
        super().__init__(bus, self.OBJECT_PATH, bus_name)
        self._fake_camera = None
        self._camera = None

    @method(DBUS_INTERFACE, in_signature="s")
    def Start(self, device_path):
        self._camera = Camera(device_path)
        self._fake_camera = FakeCamera(self._camera)
        self._camera.start()
        self._fake_camera.start()

    @method(DBUS_INTERFACE)
    def ShowFallback(self):
        self._fake_camera.source = self._camera

    @method(DBUS_INTERFACE, in_signature="n")
    def ShowLoop(self, duration):
        def thread_target():
            file_path = Path(mkstemp(suffix=".mp4", prefix="fake-webcam"))
            recording = self._camera.record(file_path)
            sleep(duration)
            recording.stop()
            self._fake_camera.source = recording.video.reverse.loop
        thread = Thread(target=thread_target)
        thread.start()

    @method(DBUS_INTERFACE, in_signature="s")
    def ShowVideo(self, file_path):
        video = Video(file_path)
        self._fake_camera.source = video
    
    @method(DBUS_INTERFACE)
    def Stop(self):
        self._fake_camera.stop()
        self._camera.stop()