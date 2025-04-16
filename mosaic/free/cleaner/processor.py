import os
from multiprocessing import Process
from pathlib import Path
from typing import Self

import numpy as np

from mosaic.free.cleaner.packer import Packer


class Processor:
    _output_pipe = Path('/tmp/mosaic-free-processor-output')

    def __init__(self, input: Packer) -> None:
        self.source = input.source
        self._input = input
        self._proc = Process(target=self._worker)

    @property
    def output(self) -> Path:
        return self._output_pipe

    def __enter__(self) -> Self:
        if not self._output_pipe.exists():
            os.mkfifo(self._output_pipe)
        return self

    def __exit__(self, type, value, traceback) -> None:
        if self._output_pipe.exists():
            self._output_pipe.unlink()

    def _worker(self) -> None:
        with open(self._output_pipe, 'wb') as pipe:
            while True:
                frame = self._input.output.get()
                if frame is None:
                    break
                out_bytes = frame.astype(np.uint8).tobytes()
                pipe.write(out_bytes)

    def run(self) -> None:
        self._proc.start()

    def wait(self) -> None:
        self._proc.join()
