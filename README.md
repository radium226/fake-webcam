# Fake Webcam
## Overview

## Install
### Requirements
* [`v4l2loopback`](https://github.com/umlaeute/v4l2loopback) to emulate the webcam
* `sudo` to escalate privilege when creating a webcam emulator
* `poetry` to handle project lifecycle, Python isolated environment, dependencies, etc. 

### Running
The simplest way for now is to do `poetry run fake-webcam daemon` followed by `poetry run fake-webcam start`. You can test that everything work with [Webcam Tests](https://fr.webcamtests.com/).

## Usage
### Daemon
* `fake-webcam daemon` to start the daemon (required to use the client)

### Client
* `fake-webcam start` to start the Fake Webcam and `fake-webcam stop` to stop it
* `fake-webcam show loop` to record a video which will be played in loop until another `fake-webcam show ...` is run
* `fake-webcam show fallback` to fallback to the `--device` defined on start
* `fake-webcam show video --file=FILE_PATH` to show display the `FILE_PATH` video

## Known Issues
* When showing a video file, the framerate is quit weird
* You need to have `sudo` with `NOPASSWD` set because we need to be `root` at some point to load the `v4l2-loopback` module
* There is a lot of `print` and `ffmpeg` is not in `-loglevel quiet`
* The `fallback` command should be named `device`
