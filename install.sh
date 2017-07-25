#!/bin/bash

# sudo -H pip3 install --ignore-installed "git+https://github.com/radium226/fake-webcam.git"

sudo -H pip3 install -r "./requirements.txt"
sudo -H pip3 install -I "$( pwd )"
