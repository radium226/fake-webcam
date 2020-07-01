#!/usr/bin/env

from .effect import Effect
from rx import operators as ops
import rx
from .draw import draw
from .svg.core import load, rasterize


class ImageOverlayEffect(Effect):

    def __init__(self, file_path, size=None, position=None):
        self._file_path = file_path
        self._size = size
        self._position = position

    def operator(self, frame_size, frame_rate):
        figures = rx.repeat_value(Figure(image=rasterize(load(self._file_path), self._size), position=self._position))
        def _image_overlay(frames):
            frames.pipe(draw(figures))

        return _image_overlay


