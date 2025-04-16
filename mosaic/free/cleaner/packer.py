from multiprocessing import Process, Queue
from pathlib import Path
from typing import Self

import numpy as np

from mosaic.free.cleaner.splitter import Splitter


class Packer:
    def __init__(self,
                 source: Splitter,
                 *,
                 maxsize: int = 1) -> None:
        self.origin = o = source.origin
        self._input = source
        self._height = o.height
        self._width = o.width
        self._frame_size = o.width * o.height * 3
        self._queue = Queue(maxsize=maxsize)
        self._proc = Process(target=self._worker)

    @property
    def input(self) -> Path:
        return self._input.output

    @property
    def output(self) -> Queue:
        return self._queue

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type, value, traceback) -> None:
        pass

    def _worker(self) -> None:
        with open(self.input, 'rb') as pipe:
            while True:
                in_bytes = pipe.read(self._frame_size)
                if not in_bytes:
                    self.output.put(None)
                    break
                frame = np.frombuffer(in_bytes, np.uint8).reshape(
                    (self._height, self._width, 3))
                self.output.put(frame)

    def run(self) -> None:
        self._proc.start()

    def wait(self) -> None:
        self._proc.join()
