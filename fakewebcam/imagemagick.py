#!/usr/bin/env python3

import subprocess as sp
from time import sleep
from tempfile import mkstemp
import io
import os

class Size:

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __str__(self):
        return "%(width)sx%(height)s"% { 'width': self.width, 'height': self.height }

class ImageMagick:

    def __init__(self, file_object):
        self._file_object = file_object

    def _convert(self, command):
        process = sp.Popen(['convert', '-'] + command + ['-'], stdin=sp.PIPE, stdout=sp.PIPE)
        stdout, stderr = process.communicate(self._file_object.read())
        process.wait()
        return io.BytesIO(stdout)

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'rb') as file_stream:
            return ImageMagick(io.BytesIO(file_stream.read()))

    def extent(self, size, background='white', gravity='center'):
        return ImageMagick(self._convert([
            '-background', background,
            '-gravity', gravity,
            '-extent', str(size)
        ]))

    def resize(self, size):
        return ImageMagick(self._convert([
            '-resize', str(size)
        ]))

    def _format(self, name='png'):
        return ImageMagick(self._convert([
            '-format', name
        ]))

    def save_as(self, file_path=None, temp=False):
        if not file_path and not temp:
            raise Exception('You got to choose, dude.')

        if temp:
            file_descriptor, file_path = mkstemp(suffix='.png')

        formatted = self._format('png')
        with os.fdopen(file_descriptor, 'wb') as file_stream:
            file_stream.write(formatted._file_object.read())

        return file_path

    def open(self):
        return self._format('png')._file_object

if __name__ == '__main__':
    ImageMagick.from_file('./qr-code.jpg').extent(Size(800, 600)).save_as('./test.png')
