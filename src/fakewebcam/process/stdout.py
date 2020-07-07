from subprocess import Popen, PIPE
import rx
from rx.core import Observer
from rx import create
from threading import Thread, Lock
from functools import partial
from rx.disposable import Disposable, CompositeDisposable
from signal import SIGQUIT
import os


def stdout(command, buffer_size=1024):
    def on_subscribe(observer, schedule = None):
        process = Popen(command, stdout=PIPE)

        def thread_target():
            for data in iter(partial(process.stdout.read, buffer_size), b""):
                observer.on_next(data)
            observer.on_completed()
            print(" <-[THREAD FINISHED]->")

        thread = Thread(target=thread_target)
        thread.start()

        def on_dispose():
            print(f"[stdout command={command}] Killing proces... ")
            process.kill()
            print(f"[stdout command={command}] Process killed! ")
            process.wait()
            observer.on_completed()
            #thread.join()

        return on_dispose

    return create(on_subscribe)