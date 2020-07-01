#!/usr/bin/env python

from .effect import effect
from .draw import Figure, draw
from .draw.draw import draw_figure_on_frame
from .ease import ease, ease_size
import easing_functions as ef
from ..core.size import Size
from ..core.position import Position

#from .svg.rx import rasterize
from .svg.rx import rasterize
from rx import operators as ops
import rx

from io import BytesIO
from pathlib import Path

from easing_functions import *

@effect
def bouncing_image(frame_size, frame_rate, duration=1.5, svg_file_path=Path("./image.svg"), start_size=Size(0, 0), end_size=Size(200, 200)):
    def center_position(image):
        image_width = image.shape[1]
        image_height = image.shape[0]
        x = int((frame_size.width - image_width) / 2)
        y = int((frame_size.height - image_height) / 2)
        return Position(x, y)

    def _bouncing_image(frames):
        # We load the SVG
        svg_fileobj = BytesIO()
        with svg_file_path.open("rb") as fd:
            svg_fileobj.write(fd.read())
        svg_fileobj.seek(0)
        svg_bytes = svg_fileobj.read()

        image_sizes = ease_size(BounceEaseOut, start_size, end_size, frame_rate, duration / 2).pipe(
            ops.concat(ease_size(QuadEaseInOut, end_size, start_size, frame_rate, duration / 2))
        )
        images = image_sizes.pipe(rasterize(svg_bytes))
        figures = images.pipe(ops.map(lambda image: Figure(image, center_position(image))))

        return frames.pipe(draw(figures))
    return _bouncing_image
    