#!/usr/bin/env python

from click import group, command, option, argument, INT
from pathlib import Path

from dbus import SessionBus
from ..dbus import FakeWebcamObject, BUS_NAME

from signal import signal, SIGINT

from threading import Event

DEFAULT_DEVICE_PATH = "/dev/video0"

@group()
def run():
    pass

@run.command()
@option("--device", "device_path", default=DEFAULT_DEVICE_PATH)
def start(device_path):
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.Start(device_path)

@run.command()
def stop():
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.Stop()

@run.group()
def show():
    pass

@show.command()
@option("--duration", "duration", default=30)
def loop(duration):
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.ShowLoop(duration)

@show.command()
def fallback():
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.ShowFallback()

@show.command()
@option("--url", "url", required=True)
def youtube(url):
    pass

@show.command()
@option("--file", "file_path", required=True)
def video(file_path):
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.ShowVideo(file_path)

@run.group()
def effect():
    pass

@effect.command()
@option("--ratio", "ratio", type=INT, default=30)
def pixelate(ratio):
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.EffectPixelate(ratio)

@effect.command()
def none():
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.EffectNone()


'''
@camera.command()
@option("--device", "device_path", default="/dev/video0")
def start(device_path):
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, CameraObject.object_path(device_path))
    remote_object.Start()

@camera.command()
@option("--device", "device_path", default="/dev/video0")
def stop(device_path):
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, CameraObject.object_path(device_path))
    remote_object.Stop()

@camera.command()
@option("--device", "device_path", default="/dev/video0")
@argument("file_path")
def record(device_path, file_path):
    bus = SessionBus()
    remote_camera = bus.get_object(BUS_NAME, CameraObject.object_path(device_path))
    record_object_path = remote_camera.Record(str(Path(file_path).resolve()))
    event = Event()
    signal(SIGINT, lambda a, b: event.set())
    event.wait()
    print("WOLOLO")
    remote_record = bus.get_object(BUS_NAME, record_object_path)
    remote_record.Stop()
'''


# fake-webcam start --device="/dev/video0"

# fake-webcam show recording --duration=30
# fake-webcam show fallback
# fake-webcam show youtube --url=""

# fake-webcam stop