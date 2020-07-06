#!/usr/bin/env python

from rx import operators as op
import cv2

from .transformation import Transformation

class GrayTransformation(Transformation):

    def __init__(self):
        pass

    def transform(self, video_source):
        print("[transformation/gray]")
        def _gray(color_frame):
            print(f"[transformation/gray] _gray({color_frame})")
            #gray_frame = cv2.cvtColor(cv2.cvtColor(color_frame, cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2GRAY)
            #return cv2.cvtColor(cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2BGRA)
            gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

        def _subscribe(frames):
            print(f"[transformation/gray] _subscribe({frames})")
            return frames.pipe(op.map(_gray))

        return _subscribe


def gray():
    return GrayTransformation()