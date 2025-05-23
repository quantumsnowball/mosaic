from pathlib import Path
from subprocess import Popen
from typing import Self

from mosaic.upscale.upscaler.processor import Processor
from mosaic.utils.ffmpeg import FFmpeg
from mosaic.utils.progress import ProgressBar
from mosaic.utils.spec import VideoDest


class Combiner:
    def __init__(
        self,
        source: Processor,
        dest: VideoDest,
        raw_info: bool,
    ) -> None:
        self.origin = source.origin
        self._input = source
        self._scale = dest.scale
        self._output_file = dest.output_file
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
        # block until upsampled info available
        info = self._input.upsampled_info.get()

        # create the ffmpeg stream command using correct info
        ffmpeg = (
            FFmpeg()
            .global_args(
                '-y',
                '-hide_banner',
            )
            .input(
                # 0:v
                '-f', 'rawvideo',
                '-framerate', self.origin.framerate,
                '-pix_fmt', 'rgb24',
                '-s', info.s,
                '-i', str(self.input),
                # 1:a
                *self.origin.ffmpeg_input_args,
                '-i', str(self.origin),
            )
            .output(
                '-map', '0:v',
                '-map', '1:a',
                #
                '-pix_fmt', 'yuv420p',
                '-vcodec', 'libx264',
                '-vf', f'scale=-2:{self._scale.replace("p", "")}',
                '-aspect', self.origin.dar,
                str(self._output_file),
            )
        )

        # if not showing raw info, ask ffmpeg to print progress info and run progress bar
        if self._pbar:
            ffmpeg.global_args(
                '-loglevel', 'fatal',
                '-progress', str(self._pbar.input),
                '-stats_period', ProgressBar.REFRESH_RATE,
            )
            self._pbar.run()

        # run
        self._proc = ffmpeg.run_async()

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()
        if self._pbar is not None:
            self._pbar.wait()

    def stop(self) -> None:
        if self._proc is not None:
            self._proc.terminate()
