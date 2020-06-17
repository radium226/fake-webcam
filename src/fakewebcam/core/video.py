#!/usr/bin/env python

from .process import stdout
from MediaInfo import MediaInfo

def video(file_path, size, loop=False):
    loop_command_options = []
    media_info = MediaInfo(filename=str(file_path)).getInfo()
    frame_rate = float(media_info.get("videoFrameRate"))
    duration = float(media_info.get("duration"))
    loop_command_options = ["-filter_complex", f"[0]reverse[r];[0][r]concat,loop=-1:{int(frame_rate * duration) * 2},setpts=N/{int(frame_rate)}/TB"] if loop else []

    command = [
        "ffmpeg",
        "-loglevel", "quiet", 
        "-i", str(file_path)
    ] + loop_command_options + [
        "-c:v", "rawvideo", 
        "-an", 
        "-f", "image2pipe",
        "-s", f"{size.width}x{size.height}",
        "-pix_fmt", "bgr24",
        "-"
    ]
    return stdout(command, buffer_size=size.width * size.height * 3)