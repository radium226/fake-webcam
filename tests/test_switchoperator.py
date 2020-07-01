#!/usr/bin/env 

import rx
from rx import operators as op
import itertools as i

from queue import Queue
from time import sleep
from threading import Thread

def from_queue(queue):
    def on_subscribe(observer, schedule = None):
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


rx.with_latest_from

def identity():

    def subscribe(source):
        return source

    return subscribe

def double():

    def subscribe(source):
        return source.pipe(op.map(lambda item: item * 2))

    return subscribe


def triple():

    def subscribe(source):
        return source.pipe(op.map(lambda item: item * 3))

    return subscribe


def switch_operator(operators):
    def _switch_operator(source):

        def subscribe(observer, scheduler = None):
            def on_next(value):
                (item, operator) = value

                source.pipe(operator).subscribe(lambda item: observer.on_next(item))

            return source.pipe(op.combine_latest(operators)).subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler)
        return rx.create(subscribe)
    return _switch_operator


def test_switch_operator():
    numbers = rx.zip(
        rx.timer(1, 1), 
        rx.from_iterable(i.count(0)) 
    ).pipe(
        op.map(lambda t: t[1])
    )

    operator_queue = Queue()
    operators = from_queue(operator_queue)
    results = numbers.pipe(switch_operator(operators))

    def thread_target():
        sleep(2)
        operator_queue.put(double())
        sleep(2)
        operator_queue.put(triple())
        sleep(2)


    operator_queue.put(op.map(lambda item: item))

    thread = Thread(target=thread_target)
    thread.start()

    disposable = results.subscribe(lambda number: print(number))
    thread.join()
    disposable.dispose()