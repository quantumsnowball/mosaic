import json
import subprocess
from pathlib import Path
from subprocess import PIPE


class VideoStream:
    def __init__(self, data: dict) -> None:
        self._d = data

    @property
    def width(self) -> int:
        return int(self._d['width'])

    @property
    def height(self) -> int:
        return int(self._d['height'])

    @property
    def resolution(self) -> str:
        return f'{self.width}x{self.height}'

    @property
    def framerate(self) -> str:
        return str(self._d['r_frame_rate'])

    @property
    def sar(self) -> str:
        return str(self._d['sample_aspect_ratio'])

    @property
    def dar(self) -> str:
        return str(self._d['display_aspect_ratio'])

    @property
    def pix_fmt(self) -> str:
        return str(self._d['pix_fmt'])

    @property
    def duration(self) -> str:
        return str(self._d['duration'])


class FFprobe:
    _args = (
        'ffprobe',
        '-v', 'quiet',
        '-output_format', 'json',
        '-show_streams',
        '-hide_banner',
    )

    def __init__(self, input_file: Path) -> None:
        args = self._args + (str(input_file), )
        result = subprocess.run(args, stdout=PIPE, stderr=PIPE, text=True)
        raw_data = json.loads(result.stdout)
        self.streams = raw_data['streams']

    @property
    def video(self) -> tuple[VideoStream, ...]:
        if len(self.streams) <= 0:
            raise ValueError("No video stream found.")
        return tuple(VideoStream(s)
                     for s in self.streams
                     if s['codec_type'] == 'video')
