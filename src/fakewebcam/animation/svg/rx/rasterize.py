#!/usr/bin/env python

from .. import core
from rx import operators as ops

def rasterize(svg_bytes):
    def _rasterize(sizes):
        return sizes.pipe(
            ops.map(lambda size: core.rasterize(svg_bytes, size))
        )
    return _rasterize