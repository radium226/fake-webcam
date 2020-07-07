#!/usr/bin/env python

from ..video.videoediting import VideoEditing

class NoOp(VideoEditing):

    def edit(self, video):
        return video

def noop():
    return NoOp()