import json
import subprocess
from pathlib import Path
from subprocess import PIPE

from mosaic.utils.time import HMS


class VideoStream:
    def __init__(self, data: dict) -> None:
        self._d = data

    @property
    def codec_name(self) -> str:
        return str(self._d.get('codec_name', 'n.a.'))

    @property
    def profile(self) -> str:
        return str(self._d.get('profile', 'n.a.'))

    @property
    def width(self) -> int:
        return int(self._d.get('width', -1))

    @property
    def height(self) -> int:
        return int(self._d.get('height', -1))

    @property
    def resolution(self) -> str:
        return f'{self.width}x{self.height}'

    @property
    def bit_rate(self) -> float:
        return float(self._d.get('bit_rate', -1))

    @property
    def framerate(self) -> str:
        return str(self._d.get('r_frame_rate', 'n.a.'))

    @property
    def avg_framerate(self) -> str:
        return str(self._d.get('avg_frame_rate', 'n.a.'))

    @property
    def sar(self) -> str:
        return str(self._d.get('sample_aspect_ratio', 'n.a.'))

    @property
    def dar(self) -> str:
        return str(self._d.get('display_aspect_ratio', 'n.a.'))

    @property
    def pix_fmt(self) -> str:
        return str(self._d.get('pix_fmt', 'n.a.'))

    @property
    def duration(self) -> str:
        return str(self._d.get('duration', 'n.a.'))

    @property
    def hms(self) -> HMS:
        return HMS.from_total_seconds(round(float(self.duration)))

    @property
    def summary(self) -> tuple[str, ...]:
        return (
            f'{self.codec_name} ({self.profile})',
            f'{self.resolution} [SAR {self.sar} DAR {self.dar}]',
            f'{self.bit_rate/1e3} kb/s',
            f'{round(eval(self.framerate), 2)} fps',
        )


class AudioStream:
    def __init__(self, data: dict) -> None:
        self._d = data

    @property
    def codec_name(self) -> str:
        return str(self._d.get('codec_name', 'n.a.'))

    @property
    def profile(self) -> str:
        return str(self._d.get('profile', 'n.a.'))

    @property
    def sample_rate(self) -> str:
        return str(self._d.get('sample_rate', 'n.a.'))

    @property
    def channel_layout(self) -> str:
        return str(self._d.get('channel_layout', 'n.a.'))

    @property
    def bit_rate(self) -> float:
        return float(self._d.get('bit_rate', -1))

    @property
    def duration(self) -> str:
        return str(self._d.get('duration', 'n.a.'))

    @property
    def hms(self) -> HMS:
        return HMS.from_total_seconds(round(float(self.duration)))

    @property
    def summary(self) -> tuple[str, ...]:
        return (
            f'{self.codec_name} ({self.profile})',
            f'{self.sample_rate} Hz',
            f'{self.channel_layout}',
            f'{self.bit_rate/1e3} kb/s',
        )


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

    @property
    def audio(self) -> tuple[AudioStream, ...]:
        return tuple(AudioStream(s)
                     for s in self.streams
                     if s['codec_type'] == 'audio')
