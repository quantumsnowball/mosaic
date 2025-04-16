import os
from pathlib import Path
from subprocess import Popen

import ffmpeg


class Splitter:
    output_pipe = Path('/tmp/mosaic-free-splitter-output')

    def __init__(self,
                 input_file: Path,
                 **input_kwargs) -> None:
        if not self.output_pipe.exists():
            os.mkfifo(self.output_pipe)
        self._stream = (
            ffmpeg
            .input(str(input_file), **input_kwargs)
            .output(str(self.output_pipe),
                    format='rawvideo',
                    pix_fmt='rgb24')
            .global_args(
                '-y',
                '-hide_banner',
                '-loglevel', 'quiet')
        )
        self._proc: Popen | None = None

    def run(self) -> None:
        self._proc = self._stream.run_async(pipe_stdout=False)

    def wait(self) -> None:
        assert self._proc is not None
        self._proc.wait()
