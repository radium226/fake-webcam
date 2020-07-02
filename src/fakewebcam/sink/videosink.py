#!/usr/bin/env python

from abc import ABC, abstractmethod


class VideoSink(ABC):

    @property
    def frames(self):
        pass

