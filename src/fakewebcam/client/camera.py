#!/usr/bin/env python


from .camerarecorder import CameraRecorder

class Camera:

    def __init__(self, device_path):
        self._device_path = device_path

    
    def list_formats(self):
        pass

    def recorder(self, size, format, frame_rate):
        return CameraRecorder(self._device_path, size, format, frame_rate)