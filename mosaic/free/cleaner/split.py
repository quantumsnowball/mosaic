import os
from pathlib import Path
from typing import Any

from mosaic.free import utils
from mosaic.free.utils import ffmpeg
from mosaic.utils import HMS


def disassemble_video(temp_dir: Path,
                      start_time: HMS | None,
                      last_time: HMS | None,
                      path: Path) -> tuple[Any, list[str], int, int]:
    fps, endtime, height, width = ffmpeg.get_video_infos(path)

    ffmpeg.video2voice(path,
                       temp_dir/'voice_tmp.mp3',
                       start_time,
                       last_time)
    ffmpeg.video2image(path,
                       temp_dir/'video2image/output_%06d.jpg',
                       start_time,
                       last_time,
                       fps)
    imagepaths = os.listdir(temp_dir/'video2image')
    imagepaths.sort()
    step = {'step': 2, 'frame': 0}
    utils.savejson(temp_dir/'step.json', step)

    return fps, imagepaths, height, width
