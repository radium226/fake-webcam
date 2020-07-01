#!/usr/bin/env python

class Effect:

    _REGISTRY = {}

    @classmethod
    def by_name(cls, name):
        return cls._REGISTRY[name]


def effect(func):
    Effect._REGISTRY[func.__name__] = func
    return func
