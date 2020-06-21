#!/usr/bin/env python

from gi.repository import GLib

from dbus import SessionBus, SystemBus
from dbus.service import BusName
from dbus.mainloop.glib import DBusGMainLoop

from pathlib import Path

from ..dbus import FakeWebcamObject, BUS_NAME

from click import command, option
from pathlib import Path


@command()
@option("--device", "device_path", default="/dev/video0")
def run(device_path):
    mainloop = GLib.MainLoop()
    DBusGMainLoop(set_as_default=True)
    
    bus = SessionBus()
    bus_name = BusName(BUS_NAME, bus)
    
    FakeWebcamObject(bus, bus_name)
    
    mainloop.run()
