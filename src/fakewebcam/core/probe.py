#!/usr/bin/env python

from subprocess import run, PIPE
import json
from collections import namedtuple

from ..core.size import Size

import re


AVG_FRAME_RATE_PATTERN = re.compile("^([0-9]+)/([0-9]+)$")

Probe = namedtuple("Probe", ["size", "pixel_format", "codec", "frame_rate"])

def probe(file_path):
    ffprobe_command = [
        "ffprobe",
        "-loglevel", "quiet",
        "-print_format", "json",
        "-show_format", 
        "-show_streams", 
        str(file_path),
    ]

    data = json.loads(run(ffprobe_command, stdout=PIPE).stdout.decode("utf-8"))
    #print(data)

    width = data["streams"][0]["width"]
    height = data["streams"][0]["height"]
    size = Size(width, height)

    avg_frame_rate = data["streams"][0]["avg_frame_rate"]
    match = AVG_FRAME_RATE_PATTERN.match(avg_frame_rate)
    frame_rate = int(int(match.group(1)) / int(match.group(2)))

    pixel_format = data["streams"][0]["pix_fmt"]
    codec = data["streams"][0]["codec_name"]

    return Probe(size, pixel_format, codec, frame_rate)
