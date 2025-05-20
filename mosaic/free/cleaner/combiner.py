from pathlib import Path
from subprocess import Popen
from typing import Self

import ffmpeg

from mosaic.free.cleaner.processor import Processor
from mosaic.utils.progress import ProgressBar


class Combiner:
    def __init__(
        self,
        source: Processor,
        output_file: Path,
        raw_info: bool,
    ) -> None:
        self.origin = s = source.origin
        self._input = source
        self._stream = (
            ffmpeg.output(
                ffmpeg.input(str(self.input),
                             format='rawvideo',
                             pix_fmt='rgb24',
                             s=f'{s.width}x{s.height}',
                             framerate=s.framerate).video,
                ffmpeg.input(str(s), **s.ffmpeg_input_kwargs).audio,
                str(output_file),
                vcodec='libx264',
                pix_fmt='yuv420p')
            .global_args('-hide_banner')
            .overwrite_output()
        )
        self._proc: Popen | None = None
        self._pbar = None if raw_info else ProgressBar(self.origin.duration)

    @property
    def input(self) -> Path:
        return self._input.output

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type, value, traceback) -> None:
        pass

    def run(self) -> None:
        self._proc = self._stream.run_async(pipe_stdin=True)

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()
