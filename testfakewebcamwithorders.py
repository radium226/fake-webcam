#!/usr/bin/env python3

from fakewebcam import Player

import signal
import sys
from time import sleep

if __name__ == "__main__":
    print("Starting player")
    player = Player.start()

    # We configure the signal handler
    def signal_handler(signal, frame):
        print("Stopping player")
        player.stop()
    signal.signal(signal.SIGINT, signal_handler)

    print("Sleeping 5 seconds")
    sleep(5)

    print("Playing a first image for 2 seconds")
    player.play_image("first-image.png", duration=2)

    print("Sleeping 5 seconds")
    sleep(5)

    print("Playing a second image for 10 seconds")
    player.play_image("second-image.png", duration=10)

    print("Sleeping 3 seconds")
    sleep(3)

    print("Playing a third image for 2 seconds")
    player.play_image("third-image.png")

    print("Waiting for player")
    player.wait_for()
