#!/usr/bin/env python

from click import ParamType
from pathlib import Path

from ..core import Camera

class CameraParamType(ParamType):
    
    name = "camera"

    def convert(self, value, param, context):
        try:
            return Camera(value)
        except Error:
            self.fail(f"unable to infer camera from {value}", param, context)

CAMERA = CameraParamType()