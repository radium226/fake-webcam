#!/usr/bin/env python

from ..common import Size
from ..video import Video

import numpy as np
import rx


def solid(color, frame_size=Size(800, 600), frame_rate=25):
    frame = np.zeros((frame_size.width, frame_size.height, 4), np.uint8)
    frame[:] = (*color, 0)
    frames = rx.repeat_value(frame)
    return Video(frames, frame_size, frame_rate)
