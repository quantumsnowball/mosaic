import os
from multiprocessing import Process
from pathlib import Path
from typing import Self

import numpy as np

from mosaic.free.cleaner.packer import Packer


class Processor:
    output_pipe = Path('/tmp/mosaic-free-processor-output')

    def __init__(self, input: Packer) -> None:
        self.source = input.source
        self._input = input
        self._proc = Process(target=self._worker)

    def __enter__(self) -> Self:
        if not self.output_pipe.exists():
            os.mkfifo(self.output_pipe)
        return self

    def __exit__(self, type, value, traceback) -> None:
        if self.output_pipe.exists():
            self.output_pipe.unlink()

    def _worker(self) -> None:
        with open(self.output_pipe, 'wb') as pipe:
            while True:
                frame = self._input.queue.get()
                if frame is None:
                    break
                out_bytes = frame.astype(np.uint8).tobytes()
                pipe.write(out_bytes)

    def run(self) -> None:
        self._proc.start()

    def wait(self) -> None:
        self._proc.join()
