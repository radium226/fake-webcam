#!/usr/bin/env python

from .fromqueue import from_queue

from rx.operators import publish, switch_latest, concat

from queue import Queue

from .process import stdin

from .player import player

from .frame import resize

class FakeCamera:

    def __init__(self, source_fallback):
        self._queue = None
        self._source_fallback = source_fallback
        self._source = source_fallback

    def _get_source(self):
        return self._source

    def _set_source(self, source):
        self._queue.put(source.frames.pipe(resize(self.size), concat(self._source_fallback.frames)))
        self._source = source

    source = property(_get_source, _set_source)

    @property
    def size(self):
        return self._source_fallback.size

    def start(self, dry=False):
        # FIXME: Handle non-dry
        ffmpeg_stdin = player(self.size)#stdin([])
        self._queue = Queue()
        self._disposable = from_queue(self._queue).pipe(switch_latest(), ffmpeg_stdin).subscribe()
        self._queue.put(self._source_fallback.frames)

    def stop(self):
        self._disposable.dispose()
        self._queue = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()