#!/bin/env python

from setuptools import setup
from glob import glob

data_files = []
directories = glob("fakewebcam/data/**/*")
for directory in directories:
    files = glob(directory+'*')
    data_files.append((directory, files))

print(data_files)

setup(
    name="fake-webcam",
    version="0.1",
    description="A small tool to fake a webcam",
    url="https://github.com/radium226/fake-webcam",
    license="GPL",
    packages=["fakewebcam"],
    package_data={
        "player": ["data/**/*", "data/static/*"]},
    zip_safe=True,
    install_requires=[
        "qrcode",
        "cherrypy"
    ],
    scripts=["scripts/fake-webcam"]
)
