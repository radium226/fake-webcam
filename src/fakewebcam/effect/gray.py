#!/usr/bin/env python

from rx import operators as op
import cv2

from .effect import Effect

class GrayEffect(Effect):

    def __init__(self):
        pass

    def operator(self, frame_size, frame_rate):
        print("[effect/gray]")
        def _gray(color_frame):
            print(f"[effect/gray] _gray({color_frame})")
            #gray_frame = cv2.cvtColor(cv2.cvtColor(color_frame, cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2GRAY)
            #return cv2.cvtColor(cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2BGRA)
            gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

        def _subscribe(frames):
            print(f"[effect/gray] _subscribe({frames})")
            return frames.pipe(op.map(_gray))

        return _subscribe
