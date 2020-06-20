#!/usr/bin/env python

import cv2
import rx.operators as op

def resize(size):
    def _resize(frame):
        return cv2.resize(frame, dsize=(size.width, size.height))

    def subscribe(source):
        return source.pipe(op.map(_resize))
    return subscribe