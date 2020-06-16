#!/usr/bin/env python

from subprocess import Popen, PIPE
from queue import Queue
from threading import Thread
from functools import partial

import numpy as np

from .recording import Recording

class CameraRecorder:

    def __init__(self, device_path, size, format, frame_rate):
        self._device_path = device_path
        self._format = format
        self._size = size
        self._frame_rate = frame_rate

        self._frame_queue = None
        self._enqueue_thread = None
        self._ffmpeg_process = None

        self._callbacks = []

    @property
    def size(self):
        return self._size

    @property
    def frame_rate(self):
        return self._frame_rate

    def _ffmpeg_command(self):
        return [
            "ffmpeg",
            "-loglevel", "quiet", 
            "-f", "v4l2",
            "-input_format", self._format,
            "-framerate", str(self._frame_rate),
            "-video_size", f"{self._size.width}x{self._size.height}",
            "-i", str(self._device_path), 
            "-c:v", "rawvideo", 
            "-an", 
            "-f", "image2pipe",
            "-s", f"{self._size.width}x{self._size.height}",
            "-pix_fmt", "bgr24",
            "-"
        ]

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        ffmpeg_command = self._ffmpeg_command()
        print(f"ffmpeg_command={' '.join(ffmpeg_command)}")
        self._frame_queue = Queue(maxsize=1)
        self._ffmpeg_process = Popen(ffmpeg_command, stdout=PIPE)
            
        def extract_frame_thread_target():
            buffer_size = self._size.width * self._size.height * 3
            print(f"buffer_size={buffer_size}")
            for frame_bytes in iter(partial(self._ffmpeg_process.stdout.read, buffer_size), b""):
                #print("Enqueuing frame! ")
                frame = np.frombuffer(frame_bytes, np.uint8).reshape((self.size.height, self.size.width, 3))
                self._frame_queue.put(frame)

        def handle_frame_thread_target():
            while True:
                frame = self._frame_queue.get()
                if frame is None:
                    break
                for callback in self._callbacks:
                    callback(frame)
                
        self._extract_frame_thread_target = Thread(target=extract_frame_thread_target)
        self._handle_frame_thread_target = Thread(target=handle_frame_thread_target)
        
        self._extract_frame_thread_target.start()
        self._handle_frame_thread_target.start()

    def stop(self):
        self._ffmpeg_process.kill()
        self._ffmpeg_process.wait()
        self._frame_queue.put(None)
        self._extract_frame_thread_target.join()
        self._handle_frame_thread_target.join()

    def add_callback(self, callback):
        self._callbacks.append(callback)

    def remove_callback(self, callback):
        self._callbacks.remove(callback)

    def record_frame(self):
        queue = Queue(maxsize=1)

        def callback(frame):
            queue.put(frame)

        self.add_callback(callback)
        frame = queue.get()
        self.remove_callback(callback)
        return frame

    def record(self, file_path):
        return Recording(self, file_path)
