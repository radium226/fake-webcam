#!/usr/bin/env python3

from setuptools import setup
from glob import glob
import os

print("HELLO WORLD! ")

#print(glob(os.path.abspath(__file__)))

setup(
    name="fake-webcam",
    version="0.1",
    description="A small tool to fake a webcam",
    url="https://github.com/radium226/fake-webcam",
    license="GPL",
    packages=["fakewebcam"],
    zip_safe=True,
    install_requires=[
        "qrcode",
        "cherrypy"
    ],
    package_data={
        "fakewebcam": [
            "data/static/*",
            "data/index.html", # / for the ServerTree
            "data/blank.png" # Blank image for the fake webcam
        ]
    },
    scripts=["scripts/fake-webcam"]
)
