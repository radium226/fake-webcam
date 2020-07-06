#!/usr/bin/env python

from abc import ABC, abstractmethod

class VideoSink(ABC):

    @abstractmethod
    def drain(self, video):
        pass