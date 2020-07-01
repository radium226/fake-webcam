#!/usr/bin/env python

from .fromqueue import from_queue

from rx import operators as op
from rx.operators import publish, switch_latest, concat, with_latest_from, map as rx_map

from queue import Queue

from .process import stdin

from .player import player

from .frame import resize

import subprocess as sp

from pyudev import Context

from pathlib import Path

from time import sleep

import cv2

from .. import effect as ef

from rx import scheduler as sh

class FakeCamera:

    def __init__(self, source_fallback, label="Fake Camera"):
        self._source_queue = None
        self._source_fallback = source_fallback
        self._source = source_fallback
        self._label = label

    def _get_source(self):
        return self._source

    def _set_source(self, source):
        self._source_queue.put(source.frames.pipe(resize(self.size), concat(self._source_fallback.frames)))
        self._source = source

    source = property(_get_source, _set_source)

    def _get_effect(self):
        return None

    def _set_effect(self, effect):
        self._effect = effect
        self._effect_queue.put(effect)

    effect = property(_get_effect, _set_effect)

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

    def start(self, dry_run=False):
        self._install_module()
        print("FRAME_RATE = " + str(self._source_fallback.frame_rate))
        # FIXME: Handle non-dry
        sink = player(self.size, self.source.frame_rate) if dry_run else stdin([
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
        self._source_queue = Queue()
        self._effect_queue = Queue()

        # Initial values
        print("[FakeCamera/start] Putting initial values... ")
        self._effect_queue.put(ef.none())
        self._source_queue.put(self._source_fallback.frames)

        # Source
        print("[FakeCamera/start] Setting up source... ")
        source = from_queue(self._source_queue).pipe(
            op.subscribe_on(sh.NewThreadScheduler())
            op.switch_latest(), 
            op.publish()
        )

        # Effects (+ Sink)
        print("[FakeCamera/start] Setting up effects (+ sink)... ")
        self._effect_disposable = from_queue(self._effect_queue).pipe(
            op.map(lambda effect: source.pipe(operator)), 
            op.switch_latest(),
            sink,
        ).subscribe()

        print("[FakeCamera/start] Connecting source... ")
        self._source_disposable = source.connect()

    def stop(self):
        self._effect_disposable.dispose()
        self._source_disposable.dispose()

        self._source_queue = None
        self._effect_queue = None
        
        self._uninstall_module()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()