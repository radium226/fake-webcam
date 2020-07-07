#!/usr/bin/env python

from ..common import Size

# FIXME: It should be in another package
from ..core.probe import probe as old_probe
from ..core.process import stdout

from .video import Video

import rx
from rx import operators as ops

import numpy as np
import cv2


def probe(file_path):
    p = old_probe(file_path)
    return p.size, p.frame_rate

def read_file(file_path):
    frame_size, frame_rate = probe(file_path)
    command = [
        "ffmpeg",
        "-loglevel", "quiet", 
        "-i", str(file_path),
        "-c:v", "rawvideo", 
        "-an", 
        "-f", "image2pipe",
        "-s", f"{frame_size.width}x{frame_size.height}",
        "-pix_fmt", "bgr24",
        "-"
    ]
        
    frames = stdout(command, buffer_size=frame_size.width * frame_size.height * 3).pipe(
        ops.map(lambda frame_bytes: np.frombuffer(frame_bytes, np.uint8).reshape((frame_size.height, frame_size.width, 3))), 
        ops.map(lambda bgr_frame: cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2BGRA)),
    )

    return Video(frames, frame_size, frame_rate)