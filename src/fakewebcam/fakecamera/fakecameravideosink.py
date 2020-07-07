#!/usr/bin/env python

from ..video import VideoSink
from ..process import stdin

import cv2
from rx import operators as ops


class FakeCameraVideoSink(VideoSink):

    def __init__(self, device_path):
        self._device_path = device_path

    def drain(self, video):
        return video.frames.pipe(
            ops.map(lambda frame: cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)),
            stdin([
                "ffmpeg", 
                "-re", 
                "-f", "rawvideo",
                "-video_size", f"{video.frame_size.width}x{video.frame_size.height}",
                "-pixel_format", "bgr24",
                "-framerate", str(video.frame_rate), 
                "-i", "-", 
                "-vcodec", "rawvideo", 
                "-pix_fmt", "yuv420p", 
                "-f", "v4l2", 
                str(self._device_path)
            ])
        )
        