#!/usr/bin/env python

from subprocess import Popen, PIPE

class Recording:

    def __init__(self, camera_recorder, file_path):
        self._file_path = file_path
        self._camera_recorder = camera_recorder

        self._subscription = None
        self._ffmpeg_process = None

    def start(self):
        self._ffmpeg_process = Popen([
            "ffmpeg", 
                #"-loglevel", "quiet",
                "-f", "rawvideo",
                "-video_size", f"{self._camera_recorder.size.width}x{self._camera_recorder.size.height}",
                "-pixel_format", "bgr24",
                "-i", "-", 
                "-an",
                #"-codec:v", "libx264",
                "-f", "avi", 
                "-r", str(self._camera_recorder.frame_rate),
                str(self._file_path)
        ], stdin=PIPE)
        self._camera_recorder.add_callback(self.on_frame)

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def on_frame(self, frame):
        self._ffmpeg_process.stdin.write(frame.tobytes())

    def stop(self):
        self._camera_recorder.remove_callback(self.on_frame)
        self._ffmpeg_process.stdin.close()
        self._ffmpeg_process.wait()