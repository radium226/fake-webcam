#!/usr/bin/env python

from ..core import Camera, FakeCamera, Video, Effect

from dbus.service import Object, method

from time import sleep
from tempfile import mkstemp
from pathlib import Path
from threading import Thread

from ..effect import ImageOverlayEffect, GrayEffect, NoneEffect

from pathlib import Path


class FakeWebcamObject(Object):

    OBJECT_PATH = '/com/github/radium226/FakeWebcam'
    DBUS_INTERFACE = 'com.github.radium226.FakeWebcam'


    def __init__(self, bus, bus_name):
        super().__init__(bus, self.OBJECT_PATH, bus_name)
        self._fake_camera = None
        self._camera = None

    @method(DBUS_INTERFACE, in_signature="sb")
    def Start(self, device_path, dry_run):
        self._camera = Camera(device_path)
        self._fake_camera = FakeCamera(self._camera)
        self._camera.start()
        self._fake_camera.start(dry_run=dry_run)

    @method(DBUS_INTERFACE)
    def ShowFallback(self):
        self._fake_camera.source = self._camera

    @method(DBUS_INTERFACE, in_signature="n")
    def ShowLoop(self, duration):
        def thread_target():
            _, file_path = mkstemp(suffix=".mp4", prefix="fake-webcam")
            recording = self._camera.record(Path(file_path))
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
    def EffectNone(self):
        self._fake_camera.effect = Effect.identity()

    @method(DBUS_INTERFACE, in_signature="s")
    def EffectImageOverlay(self, file_path):
        self._fake_camera.effect = ImageOverlayEffect(Path(file_path))

    @method(DBUS_INTERFACE)
    def EffectGray(self):
        self._fake_camera.effect = GrayEffect()

    @method(DBUS_INTERFACE)
    def EffectNone(self):
        self._fake_camera.effect = NoneEffect()

    @method(DBUS_INTERFACE)
    def Stop(self):
        self._fake_camera.stop()
        self._camera.stop()