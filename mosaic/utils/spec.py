from pathlib import Path
from typing import Any

import ffmpeg

from mosaic.utils import HMS


class VideoSource:
    def __init__(
        self,
        input_file: Path,
        start_time: HMS | None = None,
        end_time: HMS | None = None,
    ) -> None:
        ffprobe_info = ffmpeg.probe(str(input_file))
        for stream in ffprobe_info['streams']:
            if stream['codec_type'] == 'video':
                self.width = int(stream['width'])
                self.height = int(stream['height'])
                self.framerate = str(stream['r_frame_rate'])
                self.sar = str(stream['sample_aspect_ratio'])
                self.dar = str(stream['display_aspect_ratio'])
                self.pix_fmt = str(stream['pix_fmt'])
                self._duration = str(stream['duration'])
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
    def duration(self) -> float:
        # duration is end_time seconds or full vidoe seconds
        try:
            duration = self.end_time.total_seconds() if self.end_time else float(self._duration)
        except Exception:
            # default fail safe duration 5 min
            return 300
        # then deducted by start_time seconds if available
        try:
            if self.start_time:
                duration -= self.start_time.total_seconds()
        except Exception:
            pass
        #
        return duration

    @property
    def ffmpeg_input_kwargs(self) -> dict[str, Any]:
        raw_kwargs = dict(ss=self.start_time, to=self.end_time)
        filtered_kwargs = {k: v
                           for k, v in raw_kwargs.items()
                           if v is not None}
        return filtered_kwargs

    @property
    def ffmpeg_input_args(self) -> list[str]:
        raw_args: list[str | HMS | None] = ['-ss', self.start_time,
                                            '-to', self.end_time]
        filtered_args = [str(v)
                         for v in raw_args
                         if v is not None]
        return filtered_args


class VideoDest:
    def __init__(
        self,
        output_file: Path,
        scale: str
    ) -> None:
        self.output_file = output_file
        self.scale = scale.replace('p', '')
