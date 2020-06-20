#!/usr/bin/env python

from .fromqueue import from_queue

from rx.operators import publish, switch_latest, concat

from queue import Queue

from .process import stdin

from .player import player

from .frame import resize

import subprocess as sp

from pyudev import Context

from pathlib import Path

from time import sleep

class FakeCamera:

    def __init__(self, source_fallback, label="Fake Camera", dry=False):
        self._queue = None
        self._source_fallback = source_fallback
        self._source = source_fallback
        self._dry = dry
        self._label = label

    def _get_source(self):
        return self._source

    def _set_source(self, source):
        self._queue.put(source.frames.pipe(resize(self.size), concat(self._source_fallback.frames)))
        self._source = source

    source = property(_get_source, _set_source)

    @property
    def size(self):
        return self._source_fallback.size

    @property
    def device_path(self):
        context = Context()
        return Path(list(context.list_devices(subsystem="video4linux", ID_V4L_PRODUCT=self._label))[0].device_node)

    def _install_module(self):
        sp.run([
            "sudo", "modprobe", "v4l2loopback", 
		    "devices=1",
		    f"card_label={self._label}",
		    "exclusive_caps=1"
        ])
        sleep(1)

    def _uninstall_module(self):
        sp.run(["sudo", "modprobe", "--remove", "v4l2loopback"])

    def start(self):
        self._install_module()
        print("FRAME_RATE = " + str(self._source_fallback.frame_rate))
        # FIXME: Handle non-dry
        sink = player(self.size) if self._dry else stdin([
            "ffmpeg", 
            "-re", 
            "-f", "rawvideo",
            "-video_size", f"{self.size.width}x{self.size.height}",
            "-pixel_format", "bgr24",
            "-framerate", str(self._source_fallback.frame_rate), 
            "-i", "-", 
            "-vcodec", "rawvideo", 
            "-pix_fmt", "yuv420p", 
            "-f", "v4l2", 
            str(self.device_path)
        ])
        self._queue = Queue()
        self._disposable = from_queue(self._queue).pipe(
            switch_latest(), 
            sink
        ).subscribe()
        self._queue.put(self._source_fallback.frames)

    def stop(self):
        self._disposable.dispose()
        self._queue = None
        self._uninstall_module()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()