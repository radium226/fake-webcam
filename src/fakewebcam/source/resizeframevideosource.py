#!/usr/bin/env python

from .videosource import VideoSource
from .mapframevideosource import MapFrameVideoSource
from functools import partial

import cv2


class ResizeFrameVideoSource(MapFrameVideoSource):

    def _resize_frame(self, frame):
        return cv2.resize(frame, (self._frame_size.height, self._frame_size.width))

    def __init__(self, video_source, frame_size):
        super().__init__(video_source, self._resize_frame)
        self._frame_size = frame_size

    @property
    def frame_rate(self):
        return self._video_source.frame_rate

    @property
    def frame_size(self):
        return self._frame_size


def _resize(self, frame_size):
    return ResizeFrameVideoSource(self, frame_size)

VideoSource.resize = _resize