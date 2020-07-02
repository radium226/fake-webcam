#!/usr/bin/env python

from rx import operators as op
import rx

def draw_figure_on_frame(figure, frame):
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]
    
    image = figure.image

    x = figure.position.x
    y = figure.position.y

    if x >= frame_width or y >= frame_height:
        return frame

    h, w = image.shape[0], image.shape[1]

    if h == 0 or w == 0:
        return frame

    if x + w > frame_width:
        w = frame_width - x
        image = image[:, :w]

    if y + h > frame_height:
        h = frame_height - y
        image = image[:h]

    image_colors = image[..., :3]
    mask = image[..., 3:] / 255.0

    altered_frame = frame.copy()
    altered_frame[y:y+h, x:x+w] = (1.0 - mask) * frame[y:y+h, x:x+w] + mask * image_colors
    return altered_frame


def draw(figures):

    def _draw(frames):
        return frames.pipe(
            op.with_latest_from(figures),
            op.map(lambda pair: draw_figure_on_frame(pair[1], pair[0])),
        )

    return _draw