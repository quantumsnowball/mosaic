import os
import uuid
from pathlib import Path
from subprocess import Popen
from typing import Self

from mosaic.utils import TEMP_DIR
from mosaic.utils.ffmpeg import FFmpeg
from mosaic.utils.logging import log
from mosaic.utils.spec import VideoSource


class Splitter:
    def __init__(self, source: VideoSource) -> None:
        self._output_pipe = TEMP_DIR / f'{__name__}.{uuid.uuid4()}'
        self.origin = source
        self._ffmpeg = (
            FFmpeg()
            .global_args(
                '-y',
                '-hide_banner',
                '-loglevel', 'fatal',
            )
            .input(
                *source.ffmpeg_input_args,
                '-i', source,
            )
            .output(
                '-f', 'rawvideo',
                '-pix_fmt', 'rgb24',
                self._output_pipe,
            )
        )

        self._proc: Popen | None = None

    @property
    def output(self) -> Path:
        return self._output_pipe

    @log.info
    def __enter__(self) -> Self:
        if not self.output.exists():
            os.mkfifo(self.output)
        return self

    @log.info
    def __exit__(self, type, value, traceback) -> None:
        if self.output.exists():
            self.output.unlink()

    @log.info
    def run(self) -> None:
        self._proc = self._ffmpeg.run_async()

    @log.info
    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()

    @log.info
    def stop(self) -> None:
        if self._proc is not None:
            self._proc.terminate()
