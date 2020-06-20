#!/usr/bin/env python

from .process import stdout
from MediaInfo import MediaInfo
from .size import Size

import numpy as np
import rx.operators as op

class Video:

    def __init__(self, file_path, loop=False):
        self._file_path = file_path
        self._loop = loop

    @property
    def frames(self):
        loop_command_options = []
        media_info = MediaInfo(filename=str(self._file_path)).getInfo()
        frame_rate = float(media_info.get("videoFrameRate"))
        duration = float(media_info.get("duration"))
        size = Size(640, 480)
        loop_command_options = ["-filter_complex", f"[0]reverse[r];[0][r]concat,loop=-1:{int(frame_rate * duration) * 2},setpts=N/{int(frame_rate)}/TB"] if self._loop else []

        command = [
            "ffmpeg",
            "-loglevel", "quiet", 
            "-i", str(self._file_path)
        ] + loop_command_options + [
            "-c:v", "rawvideo", 
            "-an", 
            "-f", "image2pipe",
            "-s", f"{size.width}x{size.height}",
            "-pix_fmt", "bgr24",
            "-"
        ]
        return stdout(command, buffer_size=size.width * size.height * 3)#.pipe(op.map(lambda frame_bytes: np.frombuffer(frame_bytes, np.uint8).reshape((self.size.height, self.size.width, 3))))
    