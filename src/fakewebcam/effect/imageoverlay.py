#!/usr/bin/env

from .effect import Effect
from rx import operators as ops
import rx
from .draw import draw
from .svg.core import load, rasterize
from .draw import Figure
from .draw.draw import draw_figure_on_frame
from ..core.position import Position
from ..core.size import Size


class ImageOverlayEffect(Effect):


    def __init__(self, file_path, size=None, position=None):
        self._file_path = file_path
        self._size = size
        self._position = position

    def operator(self, frame_size, frame_rate):
        size = self._size or frame_size
        position = self._position or Position(5, 5)
        figure = Figure(image=rasterize(load(self._file_path), size), position=position)
        figures = rx.return_value(figure)
        def _image_overlay(frames):
            return frames.pipe(draw(figures))

        return _image_overlay


