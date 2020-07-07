#!/usr/bin/env

from ..video import VideoEditing, Video

from rx import operators as ops
from ..common import back_and_forth


class Loop(VideoEditing):

    def __init__(self, count):
        self._count = count

    def edit(self, video):
        return Video(
            video.frames.pipe(back_and_forth()).pipe(ops.repeat(self._count)),
            video.frame_size, 
            video.frame_rate, 
        )

def loop(count=None):
    return Loop(count)