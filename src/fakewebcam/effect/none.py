#!/usr/bin/env python

from rx import operators as op

from .effect import effect


@effect
def none():
    def _none(frames):
        return frames.pipe(op.map(lambda frame: frame))
    return _none
