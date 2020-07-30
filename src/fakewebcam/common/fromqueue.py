#!/usr/bin/env python

from rx import create
from rx.operators import subscribe_on
from rx.scheduler import NewThreadScheduler
from queue import Queue
from threading import Thread
import itertools


def from_queue(queue):
    def on_subscribe(observer, schedule = None):
        def thread_target():
            for item in iter(queue.get, None):
                print("Item get from queue! ")
                print(item)
                observer.on_next(item)
            observer.on_completed()
            print("We are here")
        
        thread = Thread(target=thread_target)

        def on_dispose():
            queue.put(None)
            print("We also are here")
                
        thread.start()
        return on_dispose

    return create(on_subscribe).pipe(subscribe_on(NewThreadScheduler()))