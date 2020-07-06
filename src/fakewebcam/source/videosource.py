#!/usr/bin/env python

from abc import ABC, abstractmethod
from functools import reduce


class VideoSource(ABC):

    @property
    @abstractmethod
    def frame_size(self):
        pass

    @property
    @abstractmethod
    def frames(self):
        pass

    @property
    @abstractmethod
    def frame_rate(self):
        pass

    def through(self, *transformations):
        return reduce(lambda video_source, transformation: transformation(video_source), transformations, self)
    