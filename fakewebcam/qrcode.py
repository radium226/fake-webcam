#!/usr/bin/env python3

from .imagemagick import ImageMagick
import qrcode
from qrcode.image.pure import PymagingImage
import os
from tempfile import mkstemp

class QRCode:

    @staticmethod
    def from_data(data):
        file_descriptor, file_path = mkstemp(suffix='.png')
        with os.fdopen(file_descriptor, 'wb') as f:
            qrcode.make(data,image_factory=PymagingImage).save(f)
        return ImageMagick.from_file(file_path)
