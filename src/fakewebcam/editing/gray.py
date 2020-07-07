#!/usr/bin/env python

from ..video.video import Video
from ..video.videoediting import VideoEditing

from rx import operators as ops

import cv2


class Gray(VideoEditing):

    def edit(self, video):
        def _gray(color_frame):
            print(f"[effect/Gray/edit] _gray({color_frame})")
            gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGRA2GRAY)
            return cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGRA)

        return Video(
            video.frames.pipe(ops.map(_gray)),
            video.frame_size, 
            video.frame_rate
        )


def gray():
    return Gray()