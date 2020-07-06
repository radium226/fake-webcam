#!/usr/bin/env python


from ..spi import Effect
from .. import Video

from rx import operators as ops

import cv2


class Resize(Effect):

    def __init__(self, frame_size):
        self._frame_size = frame_size

    def edit(self, source):
        return Video(
            source.frames.pipe(ops.map(lambda frame: cv2.resize(frame, (self._frame_size.width, self._frame_size.height)))),
            self._frame_size, 
            source.frame_rate
        )


def resize(frame_size):
    return Resize(frame_size)