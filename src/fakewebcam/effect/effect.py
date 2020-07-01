#!/usr/bin/env python

from abc import ABC, abstractmethod

class Effect(ABC):

    def operator(self, frame_size, frame_rate):
        pass