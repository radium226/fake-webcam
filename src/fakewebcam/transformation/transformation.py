#!/usr/bin/env python

from abc import ABC, abstractmethod

class Transformation(ABC):

    @abstractmethod
    def transform(self, video_source):
        pass