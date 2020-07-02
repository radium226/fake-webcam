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

from ..core.video import Video
from ..core.position import Position

from .draw.draw import draw_figure_on_frame
from .draw import Figure

from collections import namedtuple

import cv2


class OverlayEffect(Effect):

    def __init__(self, overlay, overlay_size=Size(width=300, height=150), overlay_position=Position(x=5, y=5)):
        self._overlay = overlay
        self._overlay_size = overlay_size
        self._overlay_position = overlay_position

    def operator(self, frame_size, frame_rate):
        position = self._overlay_position
       
        def _overlay(frame, overlay_frame):
            figure = Figure(cv2.cvtColor(cv2.resize(overlay_frame, (self._overlay_size.width, self._overlay_size.height)), cv2.COLOR_BGR2BGRA), position=position)
            return draw_figure_on_frame(figure, frame) 

        def _subscribe(frames):
            return rx.zip(frames, self._overlay.frames).pipe(
                ops.map(lambda pair: _overlay(*pair))
            )

        return _subscribe



