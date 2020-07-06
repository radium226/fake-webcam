#!/usr/bin/env python

from ..video.video import Video
from ..video.videoediting import VideoEditing

from rx import operators as ops

class Take(VideoEditing):

    def __init__(self, duration):
        self._duration = duration

    def edit(self, video):
        return Video(
            video.frames.pipe(
                ops.take(video.frame_rate * self._duration), 
            ),
            video.frame_size, 
            video.frame_rate, 
        )

def take(duration):
    return Take(duration)