#!/usr/bin/env python

from ..common import Size
from ..video import Video

import numpy as np
import cv2
import rx

def read_file(file_path, frame_rate=25):
    with file_path.open("rb") as fd:
        frame = cv2.imdecode(np.asarray(bytearray(fd.read()), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        frames = rx.repeat_value(frame)
        frame_size = Size(frame.shape[1], frame.shape[0])
        return Video(
            frames, 
            frame_size, 
            frame_rate,
        )