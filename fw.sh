#!/bin/bash

webcam()
{
    ffmpeg \
        -f "v4l2" \
        -i "/dev/video0" \
        -f "rawvideo" \
        -vcodec "rawvideo" \
        -pix_fmt "bgr24" \
        -f "rawvideo" \
        pipe:-
}

player()
{
    ffplay \
        -f "rawvideo" \
        -video_size "1280x720" \
        -pixel_format "bgr24" \
        -
}

fake_webcam()
{
    ffmpeg \
        -re \
        -f "rawvideo" \
        -video_size "1280x720" \
        -pixel_format "bgr24" \
        -framerate 30 \
        -i pipe:- \
        -vcodec "rawvideo" \
        -pix_fmt "yuv420p" \
        -threads "0" \
        -f "v4l2" \
        "/dev/video2"
}

webcam | fake_webcam
