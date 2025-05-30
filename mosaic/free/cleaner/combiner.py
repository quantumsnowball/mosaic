from pathlib import Path
from subprocess import Popen
from typing import Self

from mosaic.free.cleaner.processor import Processor
from mosaic.utils.ffmpeg import FFmpeg
from mosaic.utils.logging import trace
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

    @trace
    def __enter__(self) -> Self:
        if self._pbar:
            self._pbar.start()
        return self

    @trace
    def __exit__(self, type, value, traceback) -> None:
        if self._pbar:
            self._pbar.stop()

    @trace
    def start(self) -> None:
        # create the ffmpeg stream command using correct info
        ffmpeg = (
            FFmpeg()
            .global_args(
                '-hide_banner',
                '-y',
            )
            .input(
                # 0:v
                '-f', 'rawvideo',
                '-framerate', self.origin.framerate,
                '-pix_fmt', 'rgb24',
                '-s', f'{self.origin.width}x{self.origin.height}',
                '-i', self.input,
                # 1:a
                *self.origin.ffmpeg_input_args,
                '-i', self.origin,
            )
            .output(
                '-map', '0:v',
                '-map', '1:a',
                #
                '-pix_fmt', 'yuv420p',
                '-vcodec', 'libx264',
                '-vf', f'setsar=1:1',
                self._output_file,
            )
        )

        # if not showing raw info, ask ffmpeg to print progress info and run progress bar
        if self._pbar:
            ffmpeg.global_args(
                '-loglevel', 'fatal',
                '-progress', self._pbar.input,
                '-stats_period', ProgressBar.REFRESH_RATE,
            )
            self._pbar.run()

        # run
        self._proc = ffmpeg.run_async()

    @trace
    def run(self) -> None:
        self.start()
        self.wait()

    @trace
    def wait(self) -> None:
        if self._proc is not None:
            self._proc.wait()
        if self._pbar is not None:
            self._pbar.wait()

    @trace
    def stop(self) -> None:
        if self._proc is not None:
            self._proc.terminate()
