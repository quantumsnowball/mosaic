import os
from pathlib import Path
from subprocess import Popen
from typing import Self

import ffmpeg

from mosaic.upscale.upscaler.spec import VideoSource


class Splitter:
    _output_pipe = Path('/tmp/mosaic-upsacle-splitter-output')

    def __init__(self, source: VideoSource) -> None:
        self.origin = s = source
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
        if not self.output.exists():
            os.mkfifo(self.output)
        return self

    def __exit__(self, type, value, traceback) -> None:
        if self.output.exists():
            self.output.unlink()

    def run(self) -> None:
        self._proc = self._stream.run_async(pipe_stdout=False)

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()

    def stop(self) -> None:
        if self._proc is not None:
            self._proc.terminate()
