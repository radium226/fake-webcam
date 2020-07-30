#!/usr/bin/env python

from ..common import Size, print_frame_index, throttled_repeat_value

from functools import reduce
from itertools import repeat

import rx
from rx import operators as ops
from rx import scheduler as sh


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

    @classmethod
    def repeat_frame(cls, frame, frame_rate=25):
        frames = throttled_repeat_value(frame, 1 / frame_rate).pipe(
            print_frame_index("repeat_frame --> "), 
            ops.subscribe_on(sh.NewThreadScheduler())
        )
        frame_size = Size(frame.shape[1], frame.shape[0])
        return Video(
            frames, 
            frame_size, 
            frame_rate,
        )