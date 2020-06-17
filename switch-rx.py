#!/usr/bin/env python

import rx
from rx import operators as ops
from rx.core.typing import *

from time import sleep

from queue import Queue
from threading import Thread

import itertools


def from_queue(queue):
    def on_subscribe(observer: Observer, schedule = None):
        def thread_target():
            for item in iter(queue.get, None):
                observer.on_next(item)
        
        thread = Thread(target=thread_target)

        def on_dispose():
            queue.put(None)
            thread.join()
                
        thread.start()
        return on_dispose

    return rx.create(on_subscribe)


def letters():
     return rx.zip(rx.timer(1, 1), rx.from_iterable(range(ord('a'), ord('z') + 1))).pipe(ops.map(lambda tick_letter: chr(tick_letter[1])))


def numbers():
    return rx.zip(rx.timer(1, 1), rx.from_iterable(range(0, 100))).pipe(ops.map(lambda tick_number: tick_number[1]))


if __name__ == "__main__":
    queue = Queue()

    connectable_numbers = numbers().pipe(ops.publish())
    connectable_numbers.connect()

    disposable = from_queue(queue).pipe(ops.switch_latest()).subscribe(lambda item: print(item))

    #def queue_target_target():
    print(" ==> letters()")
    queue.put(letters())
    sleep(5)
    print(" ==> numbers()")
    queue.put(connectable_numbers)
    sleep(5)
    print(" ==> letters()")
    queue.put(letters())
    sleep(5)
    print(" ==> numbers()")
    queue.put(connectable_numbers)
    sleep(5)
    print(" ==> disposable()")
    disposable.dispose()
    
    #control_thread = Thread(target=control_thread_target)
    #control_thread.start()

    #control_thread.join()

    '''
    queue = Queue()

    d = from_queue(queue).subscribe(lambda x: print(x))
    print(type(d))
    sleep(1)

    queue.put("Ta mère")

    sleep(1)

    queue.put("Ton père")

    sleep(1)

    d.dispose()

    sleep(1)
'''
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