#!/usr/bin/env python

from abc import ABC, abstractmethod
from functools import reduce

class Source:

    @property
    @abstractmethod
    def frames(self):
        pass

    @property
    @abstractmethod
    def frame_rate(self):
        pass

    @property
    @abstractmethod
    def frame_size(self):
        pass


    def to(self, sink):
        return sink.drain(self)

    def through(self, *effects):
        return reduce(lambda source, effect: effect.edit(source), effects, self)