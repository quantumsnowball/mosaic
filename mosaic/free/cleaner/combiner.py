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
        self.origin = source.origin
        self._input = source
        self._output_file = output_file
        self._proc: Popen | None = None
        self._pbar = None if raw_info else ProgressBar(self.origin.duration)

    @property
    def input(self) -> Path:
        return self._input.output

    def __enter__(self) -> Self:
        if self._pbar:
            self._pbar.start()
        return self

    def __exit__(self, type, value, traceback) -> None:
        if self._pbar:
            self._pbar.stop()

    def run(self) -> None:
        # create the ffmpeg stream command using correct info
        stream = (
            ffmpeg.output(
                ffmpeg.input(str(self.input),
                             format='rawvideo',
                             pix_fmt='rgb24',
                             s=f'{self.origin.width}x{self.origin.height}',
                             framerate=self.origin.framerate).video,
                ffmpeg.input(str(self.origin), **self.origin.ffmpeg_input_kwargs).audio,
                str(self._output_file),
                vcodec='libx264',
                pix_fmt='yuv420p')
            .global_args('-hide_banner')
            .overwrite_output()
        )

        # if not showing raw info, ask ffmpeg to print progress info and run progress bar
        if self._pbar:
            stream = stream.global_args('-loglevel', 'fatal')
            stream = stream.global_args('-progress', self._pbar.input)
            stream = stream.global_args('-stats_period', ProgressBar.REFRESH_RATE)
            self._pbar.run()

        # run
        self._proc = stream.run_async()

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()
        if self._pbar is not None:
            self._pbar.wait()

    def stop(self) -> None:
        if self._proc is not None:
            self._proc.terminate()
