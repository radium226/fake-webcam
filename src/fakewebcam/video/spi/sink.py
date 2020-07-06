#!/usr/bin/env python

from abc import ABC, abstractmethod

class Sink(ABC):

    @abstractmethod
    def drain(self, source):
        pass