#!/usr/bin/env python

from subprocess import Popen, PIPE
import rx
from rx.core import Observer
from rx import create
from threading import Thread, Lock
from functools import partial
from rx.disposable import Disposable, CompositeDisposable
from signal import SIGQUIT
import os


def stdin(command):
    def operator(observable):
        def subscribe(observer, scheduler = None):
            print(f"[stdin/command={command} Creating process... ")
            process = Popen(command, stdin=PIPE)
            print(f"[stdin/command={command}] Process created! ")

            composite_disposable = CompositeDisposable()

            def thread_target():
                process.wait()
                observer.on_next(process.poll())
                observer.on_completed()

            def on_completed():
                print("[stdin] on_completed")
                print(f"[stdin/command={command}] Killing process (pid={process.pid})...")
                process.stdin.close()
                #process.send_signal(SIGQUIT)
                process.wait()
                print(f"[stdin/command={command}] Process killed! ")
            
            thread = Thread(target=thread_target)
            thread.start()

            def on_next(data):
                #print(f"[stdin/command={command}] on_next")
                if process.poll() is None:
                    #print(f"Writing data (poll={process.poll()})...")
                    try:
                        process.stdin.write(data)
                        #print(f"[stdin/command={command}] Data written! ")
                    except BrokenPipeError:
                        pass
                        #print("Data not written :(")
                else:
                    #print("[stdin] We're here! ")
                    on_completed()

            def on_error(error):
                print("[stdin] on_error")
                print(error)

            def on_dispose():
                print(f"[stdin command={command}] on_dispose")
                process.send_signal(SIGQUIT)
                process.wait()

            composite_disposable.add(Disposable(on_dispose))
            composite_disposable.add(observable.subscribe(on_next, on_error, on_completed, scheduler))
            return composite_disposable
        return rx.create(subscribe)
    return operator