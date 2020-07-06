#!/usr/bin/env python

from abc import ABC, abstractmethod


class VideoEditing(ABC):

    @abstractmethod
    def edit(self, video):
        pass