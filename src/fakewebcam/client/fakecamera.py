#!/usr/bin/env python

from .fakecameraplayer import FakeCameraPlayer

class FakeCamera:

    def __init__(self, device_path, size):
        self._device_path = device_path
        self._size = size

    @property
    def device_path(self):
        return self._device_path

    @property
    def size(self):
        return self._size

    @property
    def size(self):
        return self._size

    def player(self, size=None):
        return FakeCameraPlayer(self, size or self.size)