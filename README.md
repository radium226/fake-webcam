# Fake Webcam
## Overview

## Install

## Usage
* `fake-webcam start` to start the Fake Webcam and `fake-webcam stop` to stop it
* `fake-webcam show loop` to record a video which will be played in loop until another `fake-webcam show ...` is run
* `fake-webcam show fallback` to fallback to the `--device` defined on start
* `fake-webcam show video --file=FILE_PATH` to show display the `FILE_PATH` video

## Known Issues
* When showing a video file, the framerate is quit weird
* You need to have `sudo` with `NOPASSWD` set because we need to be `root` at some point to load the `v4l2-loopback` module
* There is a lot of `print` and `ffmpeg` is not in `-loglevel quiet`
* The `fallback` command should be named `device`
