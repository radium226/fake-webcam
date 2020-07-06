#!/usr/bin/env python

from functools import reduce


class Video:

    def __init__(self, frames, frame_size, frame_rate, alpha=False):
        self._frames = frames
        self._frame_size = frame_size
        self._frame_rate = frame_rate
        self._alpha = alpha

    @property
    def frames(self):
        return self._frames

    @property
    def alpha(self):
        return self._alpha

    @property
    def frame_size(self):
        return self._frame_size

    @property
    def frame_rate(self):
        return self._frame_rate

    def through(self, *editings):
        return reduce(lambda source, editing: editing.edit(source), editings, self)

    def to(self, video_sink):
        return video_sink.drain(self)

    def with_frames(self, frames):
        return Video(frames, self.frame_size, self.frame_rate)