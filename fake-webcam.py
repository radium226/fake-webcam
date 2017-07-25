#!/usr/bin/env python3

from fakewebcam import FakeWebcam
from server import Server

if __name__ == "__main__":
    fake_webcam = FakeWebcam.start()
    server = Server.start(fake_webcam, port=8080)
    server.wait_for()
