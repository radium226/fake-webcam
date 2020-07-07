#!/usr/bin/env python

from .ease import ease, ease_size
import easing_functions as ef
from ..common.size import Size
from ..common.position import Position

from rx import operators as ops
import rx

import numpy as np
import cv2

from ..video.videoediting import VideoEditing
from ..video.video import Video

class Bounce(VideoEditing):

    def __init__(self, duration):
        self._duration = duration

    def edit(self, video):
        frame_size = video.frame_size
        frame_rate = video.frame_rate

        start_size = Size(0, 0)
        end_size = frame_size

        duration = self._duration

        bouce_sizes = ease_size(ef.BounceEaseOut, start_size, end_size, frame_rate, duration / 2).pipe(
            ops.concat(ease_size(ef.QuadEaseInOut, end_size, start_size, frame_rate, duration / 2))
        )

        def _bounce(frame, bounce_size):
            new_frame = np.zeros((frame_size.height, frame_size.width, 4), np.uint8)
            if bounce_size.width == 0 or bounce_size.height == 0:
                return new_frame

            resized_frame = cv2.resize(frame, bounce_size)

            y = int((frame_size.height - bounce_size.height) / 2)
            x = int((frame_size.width - bounce_size.width) / 2)
            h = int(bounce_size.height)
            w = int(bounce_size.width)
            new_frame[y:y+h, x:x+w] = resized_frame
            
            return new_frame


        frames = rx.zip(video.frames, bouce_sizes).pipe(
            ops.map(lambda pair: _bounce(*pair))
        )
        return Video(frames, frame_size, frame_rate)


def bounce(duration=1.5):
    return Bounce(duration)
    