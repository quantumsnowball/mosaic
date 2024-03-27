import json
import os
import subprocess
from pathlib import Path
from typing import Any

from mosaic.utils import HMS
from mosaic.utils.progress import ffmpeg

# ffmpeg 3.4.6


def args2cmd(args):
    cmd = ''
    for arg in args:
        cmd += (str(arg)+' ')
    return cmd


def run(args,
        mode=0):

    if mode == 0:
        cmd = args2cmd(args)
        os.system(cmd)

    elif mode == 1:
        '''
        out_string = os.popen(cmd_str).read()
        For chinese path in Windows
        https://blog.csdn.net/weixin_43903378/article/details/91979025
        '''
        cmd = args2cmd(args)
        stream = os.popen(cmd)._stream
        sout = stream.buffer.read().decode(encoding='utf-8')
        return sout

    elif mode == 2:
        cmd = args2cmd(args)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sout = p.stdout.readlines()
        return sout


def video2image(videopath: Path,
                imagepath: Path,
                start_time: HMS | None,
                end_time: HMS | None,
                fps: int) -> None:
    args = ['ffmpeg-watch']
    if start_time and end_time:
        args += ['-ss', str(start_time)]
        args += ['-to', str(end_time)]
    args += ['-i', '"'+str(videopath)+'"']
    if fps != 0:
        args += ['-r', str(fps)]
    # args += ['-v', 'quiet']
    args += ['-f', 'image2', '-q:v', '-0', imagepath]
    run(args)


def video2voice(videopath: Path,
                voicepath: Path,
                start_time: HMS | None,
                end_time: HMS | None) -> None:
    args = ['ffmpeg-watch', '-i', '"'+str(videopath)+'"', '-async 1 -f mp3', '-b:a 320k']
    if start_time and end_time:
        args += ['-ss', str(start_time)]
        args += ['-to', str(end_time)]
    # args += ['-v', 'quiet']
    args += [voicepath]
    run(args)


def image2video(fps,
                imagepath,
                voicepath,
                videopath):
    os.system(f"ffmpeg-watch -v quiet -y -r {str(fps)} -i '{imagepath}' -vcodec libx264"
              f" '{os.path.split(voicepath)[0]}/video_tmp.mp4'")
    if os.path.exists(voicepath):
        os.system(f"ffmpeg-watch -v quiet -y -i '{os.path.split(voicepath)[0]}/video_tmp.mp4'"
                  f" -i '{voicepath}' -vcodec copy -acodec aac '{videopath}'")
    else:
        os.system(f"ffmpeg-watch -v quiet -y -i '{os.path.split(voicepath)[0]}/video_tmp.mp4' '{videopath}'")


def get_video_infos(videopath: Path) -> tuple[Any, float, int, int]:
    args = ['ffprobe -v quiet -print_format json -show_format -show_streams', '-i', '"'+str(videopath)+'"']
    out_string = run(args, mode=1)
    infos = json.loads(out_string)
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


def cut_video(in_path,
              start_time,
              last_time,
              out_path,
              vcodec='h265'):
    if vcodec == 'copy':
        os.system(f"ffmpeg -v quiet -ss {start_time} -t {last_time} -i '{in_path}'"
                  f" -vcodec copy -acodec copy '{out_path}'")
    elif vcodec == 'h264':
        os.system(f"ffmpeg -v quiet -ss {start_time} -t {last_time} -i '{in_path}'"
                  f" -vcodec libx264 -b 12M '{out_path}'")
    elif vcodec == 'h265':
        os.system(f"ffmpeg -v quiet -ss {start_time} -t {last_time} -i '{in_path}'"
                  f" -vcodec libx265 -b 12M '{out_path}'")


def continuous_screenshot(videopath,
                          savedir,
                          fps):
    '''
    videopath: input video path
    savedir:   images will save here
    fps:       save how many images per second
    '''
    videoname = os.path.splitext(os.path.basename(videopath))[0]
    # os.system('ffmpeg -i "'+videopath+'" -vf fps='+str(fps)+' -q:v -0 '+savedir+'/'+videoname+'_%06d.jpg')
    os.system(f"ffmpeg -i '{videopath}' -vf fps={str(fps)} -q:v -0 '{savedir}/{videoname}_%06d.jpg'")
