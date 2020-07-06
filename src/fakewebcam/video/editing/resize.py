#!/usr/bin/env python

from ..video import Video
from ..videoediting import VideoEditing

from rx import operators as ops

import cv2


class Resize(VideoEditing):

    def __init__(self, frame_size):
        self._frame_size = frame_size

    def edit(self, video):
        return Video(
            video.frames.pipe(
                ops.map(lambda frame: cv2.resize(frame, (self._frame_size.width, self._frame_size.height)))
            ),
            self._frame_size, 
            video.frame_rate,
        )


def resize(frame_size):
    return Resize(frame_size)