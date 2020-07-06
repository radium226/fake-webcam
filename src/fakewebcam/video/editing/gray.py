#!/usr/bin/env python

from ..videoediting import VideoEditing
from ..video import Video

from rx import operators as ops

import cv2


class Gray(VideoEditing):

    def edit(self, video):
        def _gray(color_frame):
            print(f"[effect/Gray/edit] _gray({color_frame})")
            gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

        return Video(
            video.frames.pipe(ops.map(_gray)),
            video.frame_size, 
            video.frame_rate
        )


def gray():
    return Gray()