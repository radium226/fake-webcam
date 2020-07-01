#!/usr/bin/env python

from rx import operators as op

from .effect import effect


@effect
def none(frame_size, frame_rate):
    def _none(frames):
        return frames.pipe(op.map(lambda frame: frame))
    return _none
