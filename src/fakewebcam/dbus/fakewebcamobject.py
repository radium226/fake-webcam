#!/usr/bin/env python


from dbus.service import Object, method
from pathlib import Path
from ..fakewebcam import FakeWebcam

class FakeWebcamObject(Object):

    OBJECT_PATH = '/com/github/radium226/FakeWebcam'
    DBUS_INTERFACE = 'com.github.radium226.FakeWebcam'


    def __init__(self, bus, bus_name):
        super().__init__(bus, self.OBJECT_PATH, bus_name)
        self._fake_webcam = None

    @method(DBUS_INTERFACE, in_signature="sb")
    def Start(self, device_path, dry_run):
        self._fake_webcam = FakeWebcam(Path(device_path), dry_run)
        self._fake_webcam.start()

    @method(DBUS_INTERFACE)
    def ShowDefault(self):
        self._fake_webcam.show_default()

    @method(DBUS_INTERFACE, in_signature="n")
    def ShowLoop(self, duration):
        self._fake_webcam.show_loop(duration)

    @method(DBUS_INTERFACE, in_signature="s")
    def ShowBouncingImage(self, image_file_path):
        self._fake_webcam.show_bouncing_image(Path(image_file_path))

    @method(DBUS_INTERFACE)
    def Stop(self):
        self._fake_webcam.stop()