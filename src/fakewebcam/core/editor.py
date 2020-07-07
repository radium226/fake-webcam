#!/usr/bin/env python

from .fromqueue import from_queue

from rx import operators as ops

from queue import Queue

from .process import stdin

import subprocess as sp

from pyudev import Context

from pathlib import Path

from time import sleep

import cv2

from rx import scheduler as sh

from ..editing import concat, resize, noop
from ..video import play, Video

from rx.disposable import CompositeDisposable


class Editor:

    def __init__(self, default_video, video_sink):
        self._video_queue = None
        self._editing_queue = None

        self._default_video = default_video
        self._video_sink = video_sink

    def switch_video(self, video):
        self._video_queue.put(
            video.through(resize(self.frame_size), concat(self._default_video))
        )

    def switch_editing(self, editing):
        self._editing_queue.put(editing)

    @property
    def frame_size(self):
        return self._default_video.frame_size

    @property
    def frame_rate(self):
        return self._default_video.frame_rate

    @property
    def device_path(self):
        context = Context()
        return Path(list(context.list_devices(subsystem="video4linux", ID_V4L_PRODUCT=self._label))[0].device_node)

    def start(self):
        self._disposable = CompositeDisposable()

        self._video_queue = Queue()
        self._video_queue.put(self._default_video)

        self._editing_queue = Queue()
        self._editing_queue.put(noop())

        frames = from_queue(self._video_queue).pipe(
            ops.subscribe_on(sh.NewThreadScheduler()),
            ops.map(lambda video: video.frames),
            ops.switch_latest(), 
            ops.publish()
        )
        
        self._disposable.add(frames.connect())

        video = Video(frames, self.frame_size, self.frame_rate)

        edited_video = Video(from_queue(self._editing_queue).pipe(
            ops.map(lambda editing: video.through(editing, concat(video)).frames), 
            ops.switch_latest(), 
        ), self.frame_size, self.frame_rate)

        self._disposable.add(edited_video.to(self._video_sink).subscribe())

    def stop(self):
        self._disposable.dispose()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()