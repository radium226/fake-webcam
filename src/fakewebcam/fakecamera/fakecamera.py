#!/usr/bin/env python

from .fakecameravideosink import FakeCameraVideoSink

from pyudev import Context
from pathlib import Path
import subprocess as sp

from time import sleep


class FakeCamera:

    def __init__(self, label="Fake Camera"):
        self._label = label

    @property
    def device_path(self):
        context = Context()
        return Path(list(context.list_devices(subsystem="video4linux", ID_V4L_PRODUCT=self._label))[0].device_node)

    @property
    def video_sink(self):
        return FakeCameraVideoSink(self.device_path)

    def start(self):
        self.install_module()

    def stop(self):
        self.uninstall_module()

    def install_module(self):
        sp.run([
            "sudo", "modprobe", "v4l2loopback", 
		    "devices=1",
		    f"card_label={self._label}",
		    "exclusive_caps=1"
        ])
        sleep(1)

    def uninstall_module(self):
        sp.run(["sudo", "modprobe", "--remove", "v4l2loopback"])
