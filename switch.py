#!/usr/bin/env python

from abc import ABC, abstractmethod
from enum import Enum
from subprocess import Popen, PIPE
from threading import Thread, Lock, Event
from queue import Queue, Empty
from functools import partial

from time import sleep

SENTINEL = None


from contextlib import contextmanager

class RWLock(object):
    """ RWLock class; this is meant to allow an object to be read from by
        multiple threads, but only written to by a single thread at a time. See:
        https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock
        Usage:
            from rwlock import RWLock
            my_obj_rwlock = RWLock()
            # When reading from my_obj:
            with my_obj_rwlock.r_locked():
                do_read_only_things_with(my_obj)
            # When writing to my_obj:
            with my_obj_rwlock.w_locked():
                mutate(my_obj)
    """

    def __init__(self):

        self.w_lock = Lock()
        self.num_r_lock = Lock()
        self.num_r = 0

    # ___________________________________________________________________
    # Reading methods.

    def r_acquire(self):
        self.num_r_lock.acquire()
        self.num_r += 1
        if self.num_r == 1:
            self.w_lock.acquire()
        self.num_r_lock.release()

    def r_release(self):
        assert self.num_r > 0
        self.num_r_lock.acquire()
        self.num_r -= 1
        if self.num_r == 0:
            self.w_lock.release()
        self.num_r_lock.release()

    @contextmanager
    def r_locked(self):
        """ This method is designed to be used via the `with` statement. """
        try:
            self.r_acquire()
            yield
        finally:
            self.r_release()

    # ___________________________________________________________________
    # Writing methods.

    def w_acquire(self):
        self.w_lock.acquire()

    def w_release(self):
        self.w_lock.release()

    @contextmanager
    def w_locked(self):
        """ This method is designed to be used via the `with` statement. """
        try:
            self.w_acquire()
            yield
        finally:
            self.w_release()

class SourceDisconnected(Exception):
    pass

class SinkDisconnected(Exception):
    pass

class DataTimeout(Exception):
    pass

class Status(Enum):

    CONNECTED = 1
    DISCONNECTED = 2

    SWITCHING_SOURCE = 3


class Source(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def read_data(self, buffer_size):
        pass

    @abstractmethod
    def disconnect(self):
        pass


class Sink(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def write_data(self, bytes):
        pass

    @abstractmethod
    def disconnect(self):
        pass


class ProcessSink(Sink):

    def __init__(self, command):
        self._command = command
        self._status = Status.DISCONNECTED
        self._process = None

    def connect(self):
        self._process = Popen(self._command, stdin=PIPE)
        self._status = Status.CONNECTED

    def write_data(self, data):
        if self._status == Status.CONNECTED:
            print(f"[ProcessSink/write_data] data={data}")
            self._process.stdin.write(data)
            self._process.stdin.flush()
        else:
            raise SinkDisconnected()

    def disconnect(self):
        self._status = Status.DISCONNECTED
        self._process.stdin.close()
        self._process.kill()
        self._process.wait()


class ProcessSource(Source):

    def __init__(self, command, buffer_size=5):
        self._command = command
        self._status = Status.DISCONNECTED
        self._process = None
        self._put_thread = None
        self._buffer_size = buffer_size
        self._data_queue = Queue(maxsize=1)

    def connect(self):
        #print("[ProcessSource/connect] Connecting... ")
        self._process = Popen(self._command, stdout=PIPE)

        def put_thread_target():
            for data in iter(partial(self._process.stdout.read, self._buffer_size), b""):
                #print(f"[ProcessSource/put_thread_target/command={self._command}] data={data}")
                if not data:
                    break
                self._data_queue.put(data)

        self._put_thread = Thread(target=put_thread_target)
        self._status = Status.CONNECTED
        self._put_thread.start()
        #print("[ProcessSource/connect] Connected! ")

    def read_data(self):
        if self._status == Status.DISCONNECTED:
            raise SourceDisconnected()
        
        while True:
            try:
                data = self._data_queue.get(timeout=.125)
                #print(f"data={data}")
                if not data:
                    raise SourceDisconnected()
                else:
                    return data
            except Empty:
                print("[ProcessSource/read_data/except] Raise! ")
                raise DataTimeout()

    def disconnect(self):
        self._status = Status.DISCONNECTED
        print("[ProcessSource/connect] Killing... ")
        self._process.kill()
        print("[ProcessSource/connect] Killed!... ")
        print("[ProcessSource/connect] Waiting... ")
        self._process.wait()
        print("[ProcessSource/connect] Waited! ")
        print("[ProcessSource/connect] Joining... ")
        self._put_thread.join()
        print("[ProcessSource/connect] Joined! ") 

class NullSource(Source):

    def __init__(self):
        self._event = Event()
        self._status = Status.DISCONNECTED

    def connect(self):
        self._event.clear()
        self._status = Status.CONNECTED

    def read_data(self):
        if self._status == Status.DISCONNECTED:
            raise SourceDisconnected()

        raise DataTimeout()

    def disconnect(self):
        self._status = Status.DISCONNECTED
        self._event.set()


class NullSink(Sink):

    def __init__(self):
        self._status = Status.DISCONNECTED

    def connect(self):
        self._status = Status.CONNECTED

    def write_data(self):
        if self._status == Status.DISCONNECTED:
            raise SourceDisconnected()

    def disconnect(self):
        self._status = Status.DISCONNECTED


class Pipe:

    def __init__(self, source=NullSource(), sink=NullSink()):
        self._source = source
        self._sink = sink
        self._status = Status.DISCONNECTED
        self._loop_thread = None
        self._lock = RWLock()

    def connect(self):
        if self._status == Status.CONNECTED:
            raise Error()

        def loop_thread_target():
            while True:
                print("[Pipe/connect/loop_thread_target] Looping...")
                print("[Pipe/connect/loop_thread_target] Acquiring lock...")
                with self._lock.r_locked():
                    print("[Pipe/connect/loop_thread_target] Lock acquired!")
                    if self._status != Status.CONNECTED:
                        break

                    try:
                        data = self._source.read_data()
                        print(f"[Pipe/loop_thread_target] data={data}")
                        self._sink.write_data(data)
                        continue
                    except DataTimeout as e:
                        print("[Pipe/loop_thread_target] except DataTimeout as e")
                        continue

        print("[Pipe/connect] Acquiring lock...")
        with self._lock.w_locked():
            print("[Pipe/connect] Lock acquired! ")
            self._source.connect()
            self._sink.connect()
            self._loop_thread = Thread(target=loop_thread_target)
            self._status = Status.CONNECTED
            #print("[Pipe] Starting loop thread...")
            self._loop_thread.start()
            
        #print("[Pipe] Loop thread started! ")
        

    def disconnect(self):
        print("[Pipe/disconnect] Acquiring lock...")
        with self._lock.w_locked():
            print("[Pipe/disconnect] Lock acquired! ")
            self._source.disconnect()
            self._sink.disconnect()
            self._status = Status.DISCONNECTED

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, new_source):
        print("[Pipe/source] Switching source... ")
        print("[Pipe/source.setter] Acquiring lock...")
        with self._lock.w_locked():
            print("[Pipe/source.setter] Lock acquired!")
            old_source = self._source
            print(f"[Pipe/source.setter] old_source={old_source._command} / new_source={new_source._command}")
            if self._status == Status.CONNECTED:
                print(f"[Pipe/source.setter] Disconnecting old source... ")
                old_source.disconnect()
                print(f"[Pipe/source.setter] Disconnecting old source! ")
                
                print(f"[Pipe/source.setter] Connecting new source... ")
                new_source.connect()
                print(f"[Pipe/source.setter] New source connected! ")
                
            self._source = new_source
        print("[Pipe/source.setter] Source switched! ")
        
    def wait(self):
        self._loop_thread.join()


if __name__ == "__main__":
    word_source = ProcessSource(command=["./words.sh"])
    number_source = ProcessSource(command=["./numbers.sh"])
    print_sink = ProcessSink(command=["./print.sh"])

    pipe = Pipe(source = number_source, sink=print_sink)  
    pipe.connect()

    def control_thread_target():
        sleep(2)
        print("\033[92m --> word_source\033[0m")
        pipe.source = word_source
        sleep(2)
        print("\033[92m --> number_source\033[0m")
        pipe.source = number_source
        sleep(2)
        print("\033[92m --> word_source\033[0m")
        pipe.source = word_source
        sleep(2)
        print("\033[92m --> Disconnect\033[0m")
        pipe.disconnect()

    control_thread = Thread(target=control_thread_target)
    control_thread.start()

    pipe.wait()
    








