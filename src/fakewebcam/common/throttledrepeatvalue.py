#!/usr/bin/env python

from time import sleep
from threading import Event
from rx import create

def throttled_repeat_value(value, duration):
    def on_subscribe(observer, schedule = None):
        stop_event = Event()

        while not stop_event.is_set():
            print("Throttled value! ")
            observer.on_next(value)
            sleep(duration)

        print("YOYOYOY")
        observer.on_completed()

        def on_dispose():
            stop_event.set()

        return on_dispose

    return create(on_subscribe)