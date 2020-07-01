#!/usr/bin/env

from cairosvg import svg2png
from io import BytesIO
import cv2
import numpy as np


def rasterize(svg_bytes, size):
    svg_fileobj = BytesIO()
    svg_fileobj.write(svg_bytes)
    svg_fileobj.seek(0)

    png_fileobj = BytesIO()
    svg2png(file_obj=svg_fileobj, write_to=png_fileobj, output_height=size.height, output_width=size.width)
    png_fileobj.seek(0)

    return cv2.imdecode(np.asarray(bytearray(png_fileobj.read()), dtype=np.uint8), cv2.IMREAD_UNCHANGED)