#!/usr/bin/env python

from io import BytesIO

def load(file_path):
    svg_fileobj = BytesIO()
    with svg_file_path.open("rb") as fd:
        svg_fileobj.write(fd.read())
    svg_fileobj.seek(0)
    svg_bytes = svg_fileobj.read()
    return svg_bytes