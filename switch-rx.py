#!/usr/bin/env python

import rx
from rx import operators as ops
from rx.core.typing import *

from time import sleep

from queue import Queue
from threading import Thread


def from_queue(queue):
    def dispose():
        print("DiSpOsE")

    def subscribe(observer: Observer, schedule = None, disposable = None):
        print(disposable)
        def thread_target():
            while True:
                item = queue.get()
                observer.on_next(item)
        thread = Thread(target=thread_target)
        thread.start()

    return rx.create(subscribe)





if __name__ == "__main__":
    queue = Queue()

    d = from_queue(queue).subscribe(lambda x: print(x))
    print(type(d))
    sleep(1)

    queue.put("Ta mère")

    sleep(1)

    queue.put("Ton père")

    sleep(1)

    d.dispose()

    '''

    numbers = rx.zip(rx.timer(1, 1), rx.from_iterable(range(1, 100))).pipe(
        ops.map(lambda x: x[1]), 
        ops.publish()
    )

    print(type(numbers.connect()))

    numbers.pipe(ops.map(lambda x: print(f" --> {x}"))).subscribe()
    numbers.pipe(ops.map(lambda x: print(f" ==> {x}"))).subscribe()

    numbers.pipe(ops.switch_latest())

    sleep(1)

    numbers.pipe(ops.map(lambda x: print(f" ~~> {x}"))).subscribe()

    sleep(10)

    '''