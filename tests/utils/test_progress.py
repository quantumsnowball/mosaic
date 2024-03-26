from pathlib import Path

from mosaic.utils.progress import ffmpeg


def test_ffmpeg():
    ffmpeg(f'-i {Path.home()}/Videos/input.mp4'
           ' -ss 00:00:00 -to 00:00:05'
           ' -vf scale=640:480'
           ' -y'
           f' {Path.home()}/Videos/output-640x480.mp4'.split(' '),
           exp_total_secs=5)
