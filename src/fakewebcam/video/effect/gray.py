#!/usr/bin/env python


from ..spi import Effect
from .. import Video

from rx import operators as ops

import cv2


class Gray(Effect):

    def edit(self, source):
        def _gray(color_frame):
            print(f"[effect/Gray/edit] _gray({color_frame})")
            gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

        return Video(
            source.frames.pipe(ops.map(_gray)),
            source.frame_size, 
            source.frame_rate
        )


def gray():
    return Gray()