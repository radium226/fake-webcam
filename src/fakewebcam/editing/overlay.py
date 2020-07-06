#!/usr/bin/env python

from ..video.video import Video
from ..video.videoediting import VideoEditing
from ..common import Position

from ..animation.draw.figure import Figure
from ..animation.draw.draw import draw_figure_on_frame

from rx import operators as ops
import rx
import cv2


class Overlay(VideoEditing):

    def __init__(self, figures):
        self._figures = figures

    def edit(self, video):
        def _overlay(frame, figure):
            new_figure = Figure(cv2.cvtColor(figure.image, cv2.COLOR_BGR2BGRA), position=figure.position)
            return draw_figure_on_frame(new_figure, frame) 

        return Video(
            rx.zip(video.frames, self._figures).pipe(
                ops.map(lambda pair: _overlay(*pair))
            ),
            video.frame_size, 
            video.frame_rate,
        )

def overlay(video, position=Position(10, 10)):
    figures = video.frames.pipe(
        ops.map(lambda frame: Figure(frame, position))
    )
    return Overlay(figures)