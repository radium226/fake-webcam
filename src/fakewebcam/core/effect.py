#!/usr/bin/env python

import cv2
from .size import Size

class Effect:

    @classmethod
    def identity(self):
        def effect(frame):
            return frame
        return effect

    @classmethod
    def circle(self):
        def effect(frame):
            return cv2.circle(frame, (100, 100), 10, (255, 0, 0), 2)
        return effect


    @classmethod
    def pixelate(self, ratio):
        def effect(frame):
            height, width, _ = frame.shape
            return cv2.resize(cv2.resize(frame, dsize=(int(width / ratio), int(height / ratio))), dsize=(int(width), int(height)), interpolation=cv2.INTER_LINEAR)
        return effect