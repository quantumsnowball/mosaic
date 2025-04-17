import os
import time
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Self

import numpy as np

from mosaic.free.cleaner.packer import Package, Packer


class Processor:
    type InputItem = Package | None
    type Input = Queue[InputItem]

    _output_pipe = Path('/tmp/mosaic-free-processor-output')

    def __init__(self, source: Packer) -> None:
        self.origin = source.origin
        self._input = source
        self._thread = Thread(target=self._worker)

    @property
    def input(self) -> Input:
        return self._input.output

    @property
    def output(self) -> Path:
        return self._output_pipe

    def __enter__(self) -> Self:
        if not self.output.exists():
            os.mkfifo(self.output)
        return self

    def __exit__(self, type, value, traceback) -> None:
        if self.output.exists():
            self.output.unlink()

    def _worker(self) -> None:
        with open(self.output, 'wb') as output:
            while True:
                package = self.input.get()
                if package is None:
                    break
                out_bytes = package.img_origin.astype(np.uint8).tobytes()
                output.write(out_bytes)

    def run(self) -> None:
        self._thread.start()

    def wait(self) -> None:
        self._thread.join()
