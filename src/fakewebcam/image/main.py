#!/usr/bin/env python

from cairosvg import svg2png
from pathlib import Path
import numpy as np
import cv2 as cv

from io import BytesIO

import cv2
import numpy as np
import rx
from rx import operators as ops
from ..core.size import Size
from easing_functions import *

from ..core.player import player



def overlay_transparent(background, overlay, x, y):

    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
            ],
            axis = 2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    return background

def main():
    svg_image_path = Path("./image.svg")
    svg_bytes = BytesIO()
    with svg_image_path.open("rb") as fd:
        svg_bytes.write(fd.read())
    svg_bytes.seek(0)

    def rasterize(svg_bytes, size):
        svg_bytes.seek(0)
        png_bytes = BytesIO()
        svg2png(file_obj=svg_bytes, write_to=png_bytes, output_height=size.height, output_width=size.width)
        png_bytes.seek(0)
        return cv.imdecode(np.asarray(bytearray(png_bytes.read()), dtype=np.uint8), cv.IMREAD_UNCHANGED)


    def solid(size, color=(255, 0, 0)):
        solid_frame = np.zeros((size.width, size.height, 3), np.uint8)
        solid_frame[:] = color
        return rx.repeat_value(solid_frame)
    
    size = Size(500, 500)
    frame_rate = 60
    duration = 2

    start_size = Size(10, 10)
    end_size = Size(100, 100)


    def ease(factory, start, end, frame_rate, duration):
        ease = factory(start=start, end=end, duration=frame_rate * duration + 1)
        return rx.from_iterable(range(0, frame_rate * duration + 1)).pipe(ops.map(ease.ease))

    def ease_size(factory, start_size, end_size, frame_rate, duration):
        heights = ease(factory, start=start_size.height, end=end_size.height, frame_rate=frame_rate, duration=duration)
        widths = ease(factory, start=start_size.width, end=end_size.width, frame_rate=frame_rate, duration=duration)

        return widths.pipe(ops.zip(heights), ops.map(lambda t: Size(int(t[0]), int(t[1]))))
    

    def combine(svg_bytes, sizes):
        def draw_overlay(frame, size):
            print(f"size={size}")
            svg_image = rasterize(svg_bytes, size)
            #print(svg_image)
            frame_copy = frame.copy()
            overlay_transparent(frame_copy, svg_image, 200, 200)
            print(frame_copy.shape)
            return frame_copy

        def _combine(frames):
            return frames.pipe(
                ops.zip(sizes),
                ops.map(lambda t: draw_overlay(t[0], t[1])), 
                ops.map(lambda frame: cv.cvtColor(frame, cv.COLOR_BGRA2BGR))
            )

        return _combine

    image_observable = solid(size).pipe(
        combine(svg_bytes, ease_size(BounceEaseOut, start_size, end_size, frame_rate, duration).pipe(ops.concat(ease_size(QuadEaseInOut, end_size, start_size, frame_rate, duration)))), 
        player(size, frame_rate)
        
    ).run()
    
    #size_observable.subscribe(lambda s: print(s))


'''
    print(c)

    svg_image_path = Path("./image.svg")
    
    image_path = Path("./space.jpg")
    png_bytes_io = BytesIO()
    with svg_image_path.open() as fd:
        svg2png(file_obj=fd, write_to=png_bytes_io, output_height=50, output_width=50)

    png_bytes_io.seek(0)
    emoji_image_with_alpha = cv.imdecode(np.asarray(bytearray(png_bytes_io.read()), dtype=np.uint8), cv.IMREAD_COLOR)
    
    image = cv.imread(str(image_path), cv.IMREAD_COLOR)
    image_with_alpha = image #cv.cvtColor(image, cv.COLOR_BGR2BGRA)
    x = y = 200
    #image_with_alpha[x:y+emoji_image_with_alpha.shape[0], x:x+emoji_image_with_alpha.shape[1]] = emoji_image_with_alpha
    
    rx.from_iterable

    overlay_transparent(image_with_alpha, emoji_image_with_alpha, 200, 200)
    cv.imshow("coucou", image_with_alpha)
    cv.waitKey(0)  
  
    #closing all open windows  
    cv.destroyAllWindows()  
    '''