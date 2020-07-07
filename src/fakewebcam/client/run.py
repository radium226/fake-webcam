#!/usr/bin/env python


from gi.repository import GLib

from dbus import SessionBus, SystemBus
from dbus.service import BusName
from dbus.mainloop.glib import DBusGMainLoop

from pathlib import Path

from ..dbus import FakeWebcamObject, BUS_NAME

from click import command, option, group, argument, INT
from pathlib import Path

from signal import signal, SIGINT

from threading import Event

DEFAULT_DEVICE_PATH = "/dev/video0"


@group()
def run():
    pass


@run.command()
@option("--device", "device_path", default=DEFAULT_DEVICE_PATH)
@option('--dry-run', "dry_run", is_flag=True)
def start(device_path, dry_run):
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.Start(device_path, dry_run)


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
def default():
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.ShowDefault()

@show.command()
@option("--file", "file_path")
def bouncing_image(file_path):
    bus = SessionBus()
    remote_object = bus.get_object(BUS_NAME, FakeWebcamObject.OBJECT_PATH)
    remote_object.ShowBouncingImage(file_path)

@run.command()
def daemon():
    mainloop = GLib.MainLoop()
    DBusGMainLoop(set_as_default=True)
    
    bus = SessionBus()
    bus_name = BusName(BUS_NAME, bus)
    
    FakeWebcamObject(bus, bus_name)
    
    mainloop.run()
