import os
import uuid
from pathlib import Path
from subprocess import Popen
from threading import Thread
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
        self._progress_thread: Thread | None = None

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

    def _run_progress_bar(self) -> None:
        def worker() -> None:
            with (
                alive_bar(manual=True) as bar,
                open(self.progress, 'r') as progress,
            ):
                pct = 0.0
                speed_text = ''
                fps_text = ''

                def info() -> str:
                    return f'{speed_text}, {fps_text}'

                while line := progress.readline():
                    line = line.strip()
                    # track speed
                    if line.startswith('speed='):
                        speed_text = line
                        bar.text(info())
                    # track fps
                    elif line.startswith('fps='):
                        fps_text = line
                        bar.text(info())
                    # calc current time
                    elif line.startswith('out_time_us='):
                        out_time_us_text = line.split('=', maxsplit=1)[1]
                        try:
                            out_time = float(out_time_us_text) / 1e+6
                        except ValueError:
                            continue
                        # calc and show progress percentage
                        pct = out_time / self.origin.duration
                        bar(min(pct, 1.0))
                    # break on EOF or kbint
                    # if line.startswith('progress=end'):
                    #     break

                # finish bar to 100%
                bar(1.0)

        # run in own thread
        self._progress_thread = Thread(target=worker)
        self._progress_thread.start()

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
            stream = stream.global_args('-stats_period', '0.5')

        # run
        self._proc = stream.run_async()

        # if not showing raw info, display the progress bar
        if not raw_info:
            self._run_progress_bar()

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()
        if self._progress_thread is not None:
            self._progress_thread.join()
