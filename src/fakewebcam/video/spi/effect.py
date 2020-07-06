#!/usr/bin/env python

from abc import ABC, abstractmethod

class Effect(ABC):

    @abstractmethod
    def edit(self, source):
        pass