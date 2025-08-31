from pathlib import Path
from typing import Any

from mosaic.utils.ffprobe import FFprobe
from mosaic.utils.time import HMS


class VideoSource:
    def __init__(
        self,
        input_file: Path,
        start_time: HMS | None = None,
        end_time: HMS | None = None,
    ) -> None:
        # probe for the first video stream
        d = FFprobe(input_file).video[0]
        self.width = d.width
        self.height = d.height
        self.framerate = d.framerate
        self.avg_framerate = d.avg_framerate
        self.sar = d.sar
        self.dar = d.dar
        self.pix_fmt = d.pix_fmt
        self._duration = d.duration
        self.input_file = input_file
        self.start_time = start_time
        self.end_time = end_time

        # checks
        self.check_framerate()

    def __str__(self) -> str:
        return str(self.input_file)

    def check_framerate(self) -> None:
        framerate = float(eval(self.framerate))
        avg_framerate = float(eval(self.avg_framerate))
        assert 0.9 < framerate / avg_framerate < 1.1, \
            f'Incorrect video source framerate: {framerate=:.2f}, {avg_framerate=:.2f}'

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
        filtered_args: list[str] = []
        for name, val in [('-ss', self.start_time),
                          ('-to', self.end_time)]:
            if val is not None:
                filtered_args += [name, str(val)]
        return filtered_args


class VideoDest:
    def __init__(
        self,
        output_file: Path,
        scale: str
    ) -> None:
        self.output_file = output_file
        self.scale = scale.replace('p', '')
