#!/usr/bin/env python

from ..video.videoediting import VideoEditing
from ..video.video import Video

from .resize import resize

from rx import operators as ops

class Concat(VideoEditing):

    def __init__(self, video):
        self._video = video

    def edit(self, video):
        return Video(
            video.frames.pipe(
                ops.concat(self._video.through(resize(video.frame_size)).frames), 
            ),
            video.frame_size, 
            video.frame_rate,
        )

def concat(video):
    return Concat(video)