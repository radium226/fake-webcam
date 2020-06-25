#!/usr/bin/env python

from cairosvg import svg2png
from pathlib import Path
import numpy as np
import cv2 as cv

from io import BytesIO

class Image:

    @classmethod
    def load_svg(cls, file_path, size):
        png_bytes_io = BytesIO()
        with file_path.open() as fd:
            svg2png(file_obj=fd, write_to=png_bytes_io, output_width=size.width, output_height=size.height)

        png_bytes_io.seek(0)
        image = cv.imdecode(np.asarray(bytearray(png_bytes_io.read()), dtype=np.uint8), cv.IMREAD_UNCHANGED)
        return image