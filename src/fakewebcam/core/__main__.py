#!/usr/bin/env python

from .camera import camera
from .player import player
from .size import Size
from .video import video
from .fromqueue import from_queue

from rx.operators import publish, switch_latest

from queue import Queue
from threading import Thread
from time import sleep

if __name__ == "__main__":
    size = Size(960, 544)

    camera_frames = camera("/dev/video0", size=size, format="yuyv422", frame_rate=30).pipe(publish())
    connect_disposable = camera_frames.connect()

    queue = Queue()

    disposable = from_queue(queue).pipe(switch_latest()).pipe(player(size=size)).subscribe()

    def control_thread_target():
        sleep(1)
        queue.put(camera_frames)
        sleep(1)
        queue.put(video("output.mp4", size, loop=True))
        sleep(1)
        queue.put(camera_frames)
        sleep(1)
        disposable.dispose()

    control_thread = Thread(target=control_thread_target)
    control_thread.start()

    control_thread.join()
    connect_disposable.dispose()
    print("?")