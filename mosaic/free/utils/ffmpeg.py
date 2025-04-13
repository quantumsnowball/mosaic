import json
import os
from pathlib import Path
from subprocess import Popen, check_output
from typing import Any

from mosaic.utils import HMS

# ffmpeg 3.4.6


def video2image(videopath: Path,
                imagepath: Path,
                start_time: HMS | None,
                end_time: HMS | None,
                fps: int) -> None:
    args = ['ffmpeg-watch']
    if start_time and end_time:
        args += ['-ss', str(start_time)]
        args += ['-to', str(end_time)]
    args += ['-i', str(videopath)]
    if fps != 0:
        args += ['-r', str(fps)]
    args += ['-v', 'quiet']
    args += ['-f', 'image2', '-q:v', '-0', str(imagepath)]
    Popen(args).wait()


def video2voice(videopath: Path,
                voicepath: Path,
                start_time: HMS | None,
                end_time: HMS | None) -> None:
    args = ['ffmpeg-watch',
            '-i', str(videopath),
            '-async', '1',
            '-f', 'mp3',
            '-b:a', '320k']
    if start_time and end_time:
        args += ['-ss', str(start_time)]
        args += ['-to', str(end_time)]
    args += ['-v', 'quiet']
    args += [str(voicepath)]
    Popen(args).wait()


def image2video(fps: int,
                imagepath: Path,
                voicepath: Path,
                videopath: Path):
    Popen(['ffmpeg-watch',
           '-v', 'quiet',
           '-y',
           '-r', str(fps),
           '-i', str(imagepath),
           '-vcodec', 'libx264',
           str(voicepath.parent/'video_tmp.mp4')]).wait()
    if os.path.exists(voicepath):
        Popen(['ffmpeg-watch',
               '-v', 'quiet',
               '-y',
               '-i', str(voicepath.parent/'video_tmp.mp4'),
               '-i', str(voicepath),
               '-vcodec', 'copy',
               '-acodec', 'aac',
               str(videopath)]).wait()
    else:
        Popen(['ffmpeg-watch',
               '-v', 'quiet',
               '-y',
               '-i', str(voicepath.parent/'video_tmp.mp4'),
               str(videopath)]).wait()


def get_video_infos(videopath: Path) -> tuple[Any, float, int, int]:
    args = ['ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            '-i', str(videopath)]
    out_string = check_output(args)
    infos = json.loads(out_string.decode())
    try:
        fps = eval(infos['streams'][0]['avg_frame_rate'])
        endtime = float(infos['format']['duration'])
        width = int(infos['streams'][0]['width'])
        height = int(infos['streams'][0]['height'])
    except Exception as e:
        fps = eval(infos['streams'][1]['r_frame_rate'])
        endtime = float(infos['format']['duration'])
        width = int(infos['streams'][1]['width'])
        height = int(infos['streams'][1]['height'])

    return fps, endtime, height, width
