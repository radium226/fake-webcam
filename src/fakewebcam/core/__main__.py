#!/usr/bin/env python

from time import sleep

from .fakecamera import FakeCamera
from .video import Video
from .camera import Camera
from .size import Size

from .probe import probe

from .player import player
from rx import operators as op

if __name__ == "__main__":
    #print(probe("./output.mp4"))
    with Camera("/dev/video0", size=Size(320, 240)) as camera, FakeCamera(camera) as fake_camera:
        #print(fake_camera.device_path)
        sleep(5)
        recording = camera.record("./test.mp4")
        sleep(10)
        recording.stop()
        fake_camera.source = recording.video.reverse.loop
        sleep(60)

    #e2e()

    #size = Size(960, 544)
    #size = Size(640, 480)

    #camera_frames = camera("/dev/video0", size=size, format="yuyv422", frame_rate=30).pipe(publish())
    #connect_disposable = camera_frames.connect()

    #disposable = camera_frames.pipe(player(size=size)).subscribe()

    #sleep(1)

    #queue = Queue()

    #disposable = from_queue(queue).pipe(switch_latest()).pipe(player(size=size)).subscribe()

    #def control_thread_target():
    #    sleep(1)
    #    queue.put(camera_frames)
    #    sleep(1)
    #    queue.put(video("output.mp4", size, loop=True))
    #    sleep(1)
    #    queue.put(camera_frames)
    #    sleep(1)
    #    disposable.dispose()

    #control_thread = Thread(target=control_thread_target)
    #control_thread.start()

    #control_thread.join()
    #connect_disposable.dispose()
    #disposable.dispose()
    #print("?")