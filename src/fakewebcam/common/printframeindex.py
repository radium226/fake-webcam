#!/usr/bin/env python

from rx import operators as ops
from itertools import count

def print_frame_index(prefix = None):
    def _print(frame, index):
        if (index % 25 == 0):
            p = prefix or ""
            print(f"{p}Frame #{index}")

        return frame

    def _subscribe(frames):
        return frames.pipe(
            ops.zip_with_iterable(count()),
            ops.map(lambda frame_and_index: _print(*frame_and_index))
        )
    
    return _subscribe