import os
import uuid
from pathlib import Path
from subprocess import Popen
from typing import Self

import ffmpeg

from mosaic.utils.spec import VideoSource


class Splitter:
    def __init__(self, source: VideoSource) -> None:
        self._output_pipe = Path(f'/tmp/{__name__}.{uuid.uuid4()}')
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
                '-loglevel', 'fatal')
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
        self._proc = self._stream.run_async()

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()

    def stop(self) -> None:
        if self._proc is not None:
            self._proc.terminate()
