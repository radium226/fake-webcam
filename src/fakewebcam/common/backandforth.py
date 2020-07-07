#!/usr/bin/env python

import rx


def back_and_forth():
    def _back_and_forth(source):
        def subscribe(observer, scheduler = None):
            
            values = []

            def on_next(value):
                print("[reverse/subscribe/on_next] Appending value... ")
                values.append(value)
                observer.on_next(value)

            def on_completed():
                print("[reverse/subscribe/on_completed] Reversing values... ")    
                for value in reversed(values):
                    observer.on_next(value)
                observer.on_completed()

            return source.subscribe(
                on_next,
                observer.on_error,
                on_completed,
                scheduler)
        return rx.create(subscribe)
    return _back_and_forth