#!/usr/bin/env python

from .videosource import VideoSource

from rx import operators as ops


class MapFrameVideoSource(VideoSource):

    def __init__(self, video_source, frame_mapper):
        self._video_source = video_source
        self._frame_mapper = frame_mapper

    @property
    def frame_size(self):
        return self._video_source.frame_size

    @property
    def frame_rate(self):
        return self._video_source.frame_rate

    @property
    def frames(self):
        print(f"_frame_mapper={self._frame_mapper}")
        return self._video_source.frames.pipe(
            ops.map(lambda frame: self._frame_mapper(frame))
        )