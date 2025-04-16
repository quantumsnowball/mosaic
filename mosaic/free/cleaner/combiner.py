from pathlib import Path
from subprocess import Popen
from typing import Self

import ffmpeg

from mosaic.free.cleaner.processor import Processor


class Combiner:
    def __init__(self,
                 src: Processor,
                 input_file: Path,
                 output_file: Path,
                 *,
                 width: int,
                 height: int,
                 framerate: str,
                 **input_kwargs) -> None:
        self._stream = (
            ffmpeg.output(
                ffmpeg.input(str(src.output_pipe),
                             format='rawvideo',
                             pix_fmt='rgb24',
                             s=f'{width}x{height}',
                             framerate=framerate).video,
                ffmpeg.input(str(input_file), **input_kwargs).audio,
                str(output_file),
                vcodec='libx264',
                pix_fmt='yuv420p')
            .global_args('-hide_banner')
            .overwrite_output()
        )
        self._proc: Popen | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type, value, traceback) -> None:
        pass

    def run(self) -> None:
        self._proc = self._stream.run_async(pipe_stdin=True)

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()
