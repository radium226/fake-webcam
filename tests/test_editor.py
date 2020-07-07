#!/usr/bin/env python

from fakewebcam.core import Editor
from fakewebcam import video
from fakewebcam import editing
from fakewebcam import animation
from fakewebcam.common import Size

from pathlib import Path

from time import sleep


def test_editor():
    default_video = video.read_file(Path("tests/ultra-vomit.mkv")).through(editing.resize(Size(800, 600)))
    editor = Editor(default_video, video.play())

    editor.start()
    sleep(3)
    editor.stop()


def test_to_switch_video_with_editor():
    default_video = video.read_file(Path("tests/bmth.webm")).through(editing.resize(Size(800, 600)))

    alt_video = video.read_file(Path("tests/ultra-vomit.mkv")).through(editing.take(1))

    editor = Editor(default_video, video.play())

    editor.start()
    sleep(2)
    editor.switch_video(alt_video)
    sleep(2)
    editor.stop()

def test_to_switch_effect_with_editor():
    default_video = video.read_file(Path("tests/bmth.webm")).through(editing.resize(Size(800, 600)))

    alt_video = video.read_file(Path("tests/ultra-vomit.mkv")).through(editing.take(1))

    editor = Editor(default_video, video.play())

    editor.start()
    sleep(2)
    editor.switch_editing(editing.overlay(alt_video.through(animation.bounce())))
    sleep(3)
    editor.stop()