#!/bin/env python

from setuptools import setup

setup(
    name="fake-webcam",
    version="0.1",
    description="A small tool to fake a webcam",
    url="https://github.com/radium226/fake-webcam",
    license="GPL",
    packages=["fakewebcam"],
    zip_safe=True,
    install_requires=["qrcode"],
    scripts=["scripts/fake-webcam"]
)
