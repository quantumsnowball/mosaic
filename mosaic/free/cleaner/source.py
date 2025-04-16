from pathlib import Path
from typing import Any

import ffmpeg

from mosaic.utils import HMS


class VideoSource:
    def __init__(self,
                 input_file: Path,
                 start_time: HMS | None,
                 end_time: HMS | None) -> None:
        ffprobe_info = ffmpeg.probe(str(input_file))
        for stream in ffprobe_info['streams']:
            if stream['codec_type'] == 'video':
                self.width = int(stream['width'])
                self.height = int(stream['height'])
                self.framerate = str(stream['r_frame_rate'])
                break
        else:
            raise ValueError("No video stream found.")

        self.input_file = input_file
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self) -> str:
        return str(self.input_file)

    @property
    def frame_size(self) -> int:
        return self.width * self.height * 3

    @property
    def ffmpeg_input_kwargs(self) -> dict[str, Any]:
        raw_kwargs = dict(ss=self.start_time, to=self.end_time)
        filtered_kwargs = {k: v
                           for k, v in raw_kwargs.items()
                           if v is not None}
        return filtered_kwargs
