#!/usr/bin/env python3

import subprocess as sp
import threading as t
from time import sleep
from tempfile import mkstemp
import imagemagick as im
import qrcode as qr
from qrcode.image.pure import PymagingImage
import threading
import subprocess
import os
import io

from qrcode2 import QRCode

import collections as c

from queue import Queue

from imagemagick import Size

class Module:

    def __init__(self, name):
        self.name = name

    @classmethod
    def named(cls, name):
        return cls(name)

    @classmethod
    def _run_command(cls, command, sudo=True):
        return_code = sp.call(( ['sudo'] if sudo else [] ) + command)
        if (return_code > 0):
            raise Exception('The command failed')

    def insert(self, parameters=[], sudo=True):
        self._run_command(['modprobe', self.name] + parameters, sudo)

    def remove(self, sudo=True):
        self._run_command(['modprobe', '--remove', self.name], sudo)

class Order:

    STOP = 0
    PLAY_IMAGE = 1
    PLAY_VIDEO = 2

    def __init__(self, code, param=None):
        self.code = code
        self.param = param

    @classmethod
    def play_image(cls, params):
        return cls(cls.PLAY_IMAGE, params)

    @classmethod
    def play_video(cls, params):
        return cls(cls.PLAY_VIDEO, params)

    @classmethod
    def stop(cls):
        return cls(cls.STOP, None)

class State:

    CONTINUE = True
    STOP = False


class Playing:

    def __init__(self, process, on_finished_callback):
        self._on_finished_callback = on_finished_callback
        self._invoke_on_finished_callback = True
        self._process = process

        def process_thread_target():
            self._process.wait()
            if self._invoke_on_finished_callback:
                self._on_finished_callback()

        self._process_thread = threading.Thread(target=process_thread_target, args=())
        self._process_thread.start()

    @classmethod
    def for_process(cls, process, callback):
        return Playing(process, callback)

    def stop(self):
        self._invoke_on_finished_callback = False
        self._process.kill()


class Player:

    BLANK_VIDEO_FILE_PATH = './blank.png'
    SIZE = Size(800, 600)

    def __init__(self, dev_path):
        self._orders = Queue()
        self._follow_orders_thread = None
        self._current_playing = None
        self._dev_path = dev_path
        self._do_start()

    def _follow_orders(self):
        def dispatch(order):
            return {
                Order.PLAY_IMAGE: self._do_play_image,
                Order.PLAY_VIDEO: self._do_play_video,
                Order.STOP: self._do_stop
            }[order.code](order.param)

        while True:
            order = self._orders.get(block=True)
            if self._current_playing:
                self._current_playing.stop()
            if dispatch(order) == State.STOP:
                break;

    def _do_play_image(self, params):
        (file_path, duration) = params
        print(" --> Playing " + file_path + "(duration=" + str(duration) + ")")

        options = ["--loop"] if duration == 0 else ["--duration", str(duration)]

        def on_finished_callback():
            print("Calling callback of " + file_path)
            self._play_blank_image()

        ffmpeg_base_command = [
            'ffmpeg',
            '-re',
            '-loop', '1',
            '-i', file_path,
            '-vf', 'scale=iw*min(%(width)s/iw\,%(height)s/ih):ih*min(%(width)s/iw\,%(height)s/ih),pad=%(width)s:%(height)s:(%(width)s-iw)/2:(%(height)s-ih)/2' % { 'width': self.SIZE.width, 'height': self.SIZE.height },
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-f', 'v4l2']
        ffmpeg_loop_command = ['-t', str(duration)] if duration > 0 else []
        ffmpeg_command = ffmpeg_base_command + ffmpeg_loop_command + [self._dev_path]
        ffmpeg_process = subprocess.Popen(ffmpeg_command)

        self._current_playing = Playing.for_process(ffmpeg_process, on_finished_callback)
        return State.CONTINUE

    def play_image(self, file_path, duration=0):
        self._orders.put(Order.play_image((file_path, duration)))
        return State.CONTINUE

    def _play_blank_image(self):
        self._orders.put(Order.play_image((self.BLANK_VIDEO_FILE_PATH, 0)))

    def play_video(self, file_path, loop=False):
        self._orders.put(Order.play_video((file_path, loop)))

    def _do_play_video(self, params):
        (file_path, loop) = params

        def on_finished_callback():
            print("Calling callback of " + file_path)
            if loop:
                self.play_video(file_path, loop)
            else:
                self._play_blank_image()

        ffmpeg_command = [
            'ffmpeg',
                '-re',
                '-i', file_path,
                '-vf', 'scale=iw*min(%(width)s/iw\,%(height)s/ih):ih*min(%(width)s/iw\,%(height)s/ih),pad=%(width)s:%(height)s:(%(width)s-iw)/2:(%(height)s-ih)/2' % { 'width': self.SIZE.width, 'height': self.SIZE.height },
                '-vcodec', 'rawvideo',
                '-pix_fmt', 'yuv420p',
    		    '-f', 'v4l2',
                self._dev_path
        ]


#        ffmpeg_command = [
#            'ffmpeg',
#                '-re',
#                '-f', 'lavfi',
#                '-i', 'movie=filename=%(file_path)s%(loop)s, setpts=N/(FRAME_RATE*TB)' % { 'file_path': file_path, 'loop': ':loop=0' if (loop) else '' },
#                '-vf', 'scale=iw*min(%(width)s/iw\,%(height)s/ih):ih*min(%(width)s/iw\,%(height)s/ih),pad=%(width)s:%(height)s:(%(width)s-iw)/2:(%(height)s-ih)/2' % { 'width': self.SIZE.width, 'height': self.SIZE.height },
#                '-vcodec', 'rawvideo',
#                '-pix_fmt', 'yuv420p',
#    		    '-f', 'v4l2',
#                self._dev_path
#        ]
        ffmpeg_process = subprocess.Popen(ffmpeg_command)

        self._current_playing = Playing.for_process(ffmpeg_process, on_finished_callback)
        return State.CONTINUE


    @classmethod
    def start(cls, dev_path):
        return cls(dev_path)

    def _do_start(self):
        self._follow_orders_thread = threading.Thread(target=self._follow_orders, args=())
        self._follow_orders_thread.start()
        self._play_blank_image()

    def stop(self):
        self._orders.put(Order.stop())

    def _do_stop(self, params):
        print('Stopping! ')
        return State.STOP

    def wait_for(self):
        self._follow_orders_thread.join()


class FakeWebcam:

    MODULE_NAME = 'v4l2loopback'
    DEVICE_NUMBER = '0'

    def __init__(self, dev_path):
        self._module = Module.named(self.MODULE_NAME)
        self._dev_path = dev_path
        self._player = None
        self._do_start()

    @classmethod
    def start(cls):
        return cls('/dev/video%s' % cls.DEVICE_NUMBER)

    def _do_start(self):
        self._module.insert(parameters=['video_nr=%(device_number)s' % { 'device_number': self.DEVICE_NUMBER }])
        self._player = Player.start(self._dev_path)

    def play_image(self, file_path, duration=0):
        self._player.play_image(file_path, duration)

    def play_video(self, file_path, loop=False):
        self._player.play_video(file_path, loop)

    def stop(self):
        self._player.stop()
        sleep(1)
        remove_module(self.MODULE_NAME)
