import os
from pathlib import Path
from subprocess import Popen
from typing import Self

import ffmpeg

from mosaic.free.cleaner.source import VideoSource


class Splitter:
    _output_pipe = Path('/tmp/mosaic-free-splitter-output')

    def __init__(self, input: VideoSource) -> None:
        self.source = s = input
        self._stream = (
            ffmpeg
            .input(str(s), **s.ffmpeg_input_kwargs)
            .output(str(self._output_pipe),
                    format='rawvideo',
                    pix_fmt='rgb24')
            .global_args(
                '-y',
                '-hide_banner',
                '-loglevel', 'quiet')
        )
        self._proc: Popen | None = None

    @property
    def output(self) -> Path:
        return self._output_pipe

    def __enter__(self) -> Self:
        if not self._output_pipe.exists():
            os.mkfifo(self._output_pipe)
        return self

    def __exit__(self, type, value, traceback) -> None:
        if self._output_pipe.exists():
            self._output_pipe.unlink()

    def run(self) -> None:
        self._proc = self._stream.run_async(pipe_stdout=False)

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()
