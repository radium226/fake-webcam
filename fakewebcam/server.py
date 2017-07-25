#!/usr/bin/env python3

import cherrypy
import qrcode
import base64
import qrcode
from qrcode.image.pure import PymagingImage
import io
from fakewebcam import FakeWebcam
from imagemagick import Size

from qrcode2 import QRCode

class ServerTree:

    def __init__(self, fake_webcam):
        self._fake_webcam = fake_webcam

    @cherrypy.expose()
    @cherrypy.tools.allow(methods=['POST'])
    def play(self):
        data = cherrypy.request.body.read().decode('utf-8')
        base64_content = base64.b64encode(QRCode.from_data(data).open().read())
        self._fake_webcam.play_image(QRCode.from_data(data).extent(Size(800, 600)).save_as(temp=True), duration=2)
        return base64_content

    @cherrypy.expose()
    @cherrypy.tools.allow(methods=['GET'])
    def index(self, *args, **kwargs):
        return open('./static/index.html')

class Server:

    def __init__(self, fake_webcam):
        self._fake_webcam = fake_webcam

    def index(self, port):
        self.port = port

    def _start(self, port):

        cherrypy.config.update({
            "server.socket_host": "0.0.0.0",
            "server.socket_port": port
        })

        cherrypy.tree.mount(ServerTree(self._fake_webcam), '/')
        cherrypy.engine.start()

    @classmethod
    def start(cls, fake_webcam, port=8080):
        server = cls(fake_webcam)
        server._start(port)
        return server

    def stop(self):
        cherrypy.engine.exit()

    def wait_for(self):
        cherrypy.engine.block()

if __name__ == '__main__':
    fake_webcam = FakeWebcam.start()
    server = Server.start(fake_webcam, port=8080)
    server.wait_for()
