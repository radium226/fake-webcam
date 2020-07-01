#!/usr/bin/env python

from rx import operators as op

from .effect import Effect

class NoneEffect(Effect):

    def __init__(self):
        pass

    def operator(self, frame_size, frame_rate):
        def _none(frames):
            return frames.pipe(op.map(lambda frame: frame))
        return _none
