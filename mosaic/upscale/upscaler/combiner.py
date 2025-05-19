import os
import uuid
from pathlib import Path
from subprocess import Popen
from typing import Self

import ffmpeg
from alive_progress import alive_bar

from mosaic.upscale.upscaler.processor import Processor
from mosaic.upscale.upscaler.spec import VideoDest


class Combiner:
    def __init__(self,
                 source: Processor,
                 dest: VideoDest) -> None:
        self.origin = source.origin
        self._input = source
        self._scale = dest.scale
        self._output_file = dest.output_file
        self._proc: Popen | None = None
        self._progress_pipe = Path(f'/tmp/mosaic-upsacle-combiner-progress-{uuid.uuid4()}')

    @property
    def input(self) -> Path:
        return self._input.output

    @property
    def progress(self) -> Path:
        return self._progress_pipe

    def __enter__(self) -> Self:
        if not self.progress.exists():
            os.mkfifo(self.progress)
        return self

    def __exit__(self, type, value, traceback) -> None:
        if self.progress.exists():
            self.progress.unlink()

    def run(self, raw_info: bool) -> None:
        # block until upsampled info available
        info = self._input.upsampled_info.get()

        # create the ffmpeg stream command using correct info
        stream = (
            ffmpeg.output(
                ffmpeg.input(str(self.input),
                             format='rawvideo',
                             pix_fmt='rgb24',
                             s=info.s,
                             framerate=self.origin.framerate,
                             ).video,
                ffmpeg.input(str(self.origin), **self.origin.ffmpeg_input_kwargs).audio,
                str(self._output_file),
                vcodec='libx264',
                vf=f'scale=-2:{self._scale.replace("p", "")}',
                aspect=self.origin.dar,
                pix_fmt=info.pix_fmt)
            .global_args('-hide_banner')
            .overwrite_output()
        )

        # if not showing raw info, ask ffmpeg to print progress info and draw progress bar
        if not raw_info:
            stream = stream.global_args('-loglevel', 'fatal')
            stream = stream.global_args('-progress', self.progress)
            stream = stream.global_args('-stats_period', '0.1')

        # run
        self._proc = stream.run_async()

        # if not showing raw info, display the progress bar
        # FIXME: kbint not working here
        if not raw_info:
            with (
                alive_bar(manual=True) as bar,
                open(self.progress, 'r') as progress,
            ):
                pct = 0.0
                while line := progress.readline():
                    # track ffmpeg rendering speed
                    if line.strip().startswith('speed='):
                        speed_text = line.split('=', maxsplit=1)[1]
                        # calc and show speed
                        try:
                            speed = float(speed_text.replace('x', ''))
                        except ValueError:
                            continue
                        bar.text(speed_text)
                        # calc and show progress percentage
                        # TODO: determine the correct step pct, don't hardcode
                        pct += (speed * 0.1) / 5
                        bar(min(pct, 1.0))
                    # break on EOF or kbint
                    # if line.startswith('progress=end'):
                    #     break

                # finish bar to 100%
                bar(1.0)

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()
