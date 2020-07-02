#!/usr/bin/env 

import rx
from rx import operators as op
import itertools as i

from queue import Queue
from time import sleep
from threading import Thread

from rx.scheduler import NewThreadScheduler
from rx import Observable

from rx.disposable import CompositeDisposable

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

def peek(item):
    print(item)
    return item

def switch_operator(operators):
    def subscribe(cold_source):
        print("1. ")
        hot_source = cold_source.pipe(op.subscribe_on(NewThreadScheduler()), op.publish())
        print("2. ")
        disposable = hot_source.connect()
        print("3. ")
        print("4. ")

        def on_dispose():
            print("ET TA MERE")

        return operators.pipe(
            op.map(peek), 
            op.map(lambda operator: hot_source.pipe(operator)), 
            op.switch_latest(),
        )
    return subscribe


def test_switch_operator():
    numbers = rx.zip(
        rx.timer(1, 1), 
        rx.from_iterable(i.count(0)) 
    ).pipe(
        op.map(peek),
        op.map(lambda t: t[1])
    )

    operator_queue = Queue()
    operators = from_queue(operator_queue)

    def thread_target():
        sleep(2)
        print("Putting double! ")
        operator_queue.put(double())
        sleep(2)
        print("Putting triple! ")
        operator_queue.put(triple())
        sleep(2)
        operator_queue.put(None)

    operator_queue.put(op.map(lambda item: item))

    thread = Thread(target=thread_target)
    thread.start()

    disposable = numbers.pipe(switch_operator(operators)).subscribe(lambda number: print(number))

    #disposable = results.subscribe(lambda number: print(number))
    thread.join()
    disposable.dispose()
    sleep(5)
    