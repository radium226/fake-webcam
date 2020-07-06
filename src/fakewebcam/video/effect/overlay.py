#!/usr/bin/env python

from ..spi import Effect
from .. import Video
from ...common import Position
from ...effect.draw.figure import Figure
from ...effect.draw.draw import draw_figure_on_frame

from rx import operators as ops
import rx
import cv2


class Overlay(Effect):

    def __init__(self, figures):
        self._figures = figures

    def edit(self, source):
        def _overlay(frame, figure):
            new_figure = Figure(cv2.cvtColor(figure.image, cv2.COLOR_BGR2BGRA), position=figure.position)
            return draw_figure_on_frame(new_figure, frame) 

        return Video(
            rx.zip(source.frames, self._figures).pipe(
                ops.map(lambda pair: _overlay(*pair))
            ),
            source.frame_size, 
            source.frame_rate,
        )

def overlay(source, position=Position(10, 10)):
    figures = source.frames.pipe(
        ops.map(lambda frame: Figure(frame, position))
    )
    return Overlay(figures)