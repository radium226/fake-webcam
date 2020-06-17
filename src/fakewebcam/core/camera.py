#!/usr/bin/env python

from .process import stdout

def camera(device_path, size, format, frame_rate):
    command = [
        "ffmpeg",
        "-loglevel", "quiet", 
        "-f", "v4l2",
        "-input_format", format,
        "-framerate", str(frame_rate),
        "-video_size", f"{size.width}x{size.height}",
        "-i", str(device_path), 
        "-c:v", "rawvideo", 
        "-an", 
        "-f", "image2pipe",
        "-s", f"{size.width}x{size.height}",
        "-pix_fmt", "bgr24",
        "-"
    ]
    return stdout(command, buffer_size=size.width * size.height * 3)

