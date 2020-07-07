#!/usr/bin/env python

from .fromqueue import from_queue

from rx import operators as ops

from queue import Queue

from .process import stdin

from .player import player

import subprocess as sp

from pyudev import Context

from pathlib import Path

from time import sleep

import cv2

from rx import scheduler as sh

from ..editing import concat, resize
from ..video import play, Video

def peek():
    def _print(item):
        print(f"[peek] {item}")
        return item 
        
    def _peek(source):
        return source.pipe(
            op.map(_print)
        )

    return _peek


class FakeCamera:

    def __init__(self, default_video, label="Fake Camera"):
        self._video_queue = None
        self._default_video = default_video
        self._label = label

    def switch_video(self, video):
        self._video_queue.put(
            video.through(resize(self.frame_size), concat(self._default_video))
        )

    def _get_effect(self):
        return None

    def _set_effect(self, effect):
        self._effect = effect
        self._effect_queue.put(effect)

    effect = property(_get_effect, _set_effect)

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
        self._video_queue = Queue()
        self._video_queue.put(self._default_video)

        frames = from_queue(self._video_queue).pipe(
            ops.subscribe_on(sh.NewThreadScheduler()),
            ops.map(lambda video: video.frames),
            ops.switch_latest(), 
            ops.publish()
        )
        frames.connect()

        video = Video(frames, self.frame_size, self.frame_rate)

        self._video_disposable = video.to(play() if dry_run else play()).subscribe()


        '''
        self._install_module()
        print("FRAME_RATE = " + str(self._source_fallback.frame_rate))

        def v4l2(device_path, size, frame_rate):
            def _v4l2(frames):
                return frames.pipe(
                    op.map(lambda frame: cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)),
                    stdin([
                        "ffmpeg", 
                        "-re", 
                        "-f", "rawvideo",
                        "-video_size", f"{size.width}x{size.height}",
                        "-pixel_format", "bgr24",
                        "-framerate", str(frame_rate), 
                        "-i", "-", 
                        "-vcodec", "rawvideo", 
                        "-pix_fmt", "yuv420p", 
                        "-f", "v4l2", 
                        str(device_path)
                    ])
                )
            return _v4l2

        # FIXME: Handle non-dry
        sink = player(self.size, self.source.frame_rate) if dry_run else v4l2(self.device_path, self.size, self.source.frame_rate)
        self._source_queue = Queue()
        self._effect_queue = Queue()

        # Initial values
        print("[FakeCamera/start] Putting initial values... ")
        self._editing_queue.put(e.noop())
        self._video_queue.put(self._default_video)

        # Source
        print("[FakeCamera/start] Setting up source... ")
        source = from_queue(self._source_queue).pipe(
            op.subscribe_on(sh.NewThreadScheduler()),
            op.switch_latest(), 
            op.publish()
        )

        # Effects (+ Sink)
        print("[FakeCamera/start] Setting up effects (+ sink)... ")
        self._effect_disposable = from_queue(self._effect_queue).pipe(
            peek(),
            op.map(lambda effect: source.pipe(effect.operator(self.source.size, self.source.frame_rate), op.concat(source))), 
            op.switch_latest(),
            sink,
        ).subscribe()

        print("[FakeCamera/start] Connecting source... ")
        self._source_disposable = source.connect()
        '''

    def stop(self):
        self._video_disposable.dispose()
        '''
        self._source_disposable.dispose()

        self._source_queue = None
        self._effect_queue = None
        
        self._uninstall_module()
        '''

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()