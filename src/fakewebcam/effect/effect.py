#!/usr/bin/env python

from abc import ABC, abstractmethod

class Effect(ABC):

    _REGISTRY = {}

    @classmethod
    def by_name(cls, name):
        return cls._REGISTRY[name]

    def operator(self, frame_size, frame_rate):
        pass


def effect(func):
    Effect._REGISTRY[func.__name__] = func
    return func
