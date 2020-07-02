#!/usr/bin/env python

from abc import ABC, abstractmethod


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


    