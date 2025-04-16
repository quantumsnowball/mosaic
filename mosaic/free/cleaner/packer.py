from multiprocessing import Process, Queue
from typing import Self

import numpy as np

from mosaic.free.cleaner.splitter import Splitter


class Packer:
    def __init__(self,
                 input: Splitter,
                 *,
                 maxsize: int = 1) -> None:
        self.source = s = input.source
        self._input = input
        self._height = s.height
        self._width = s.width
        self._frame_size = s.width * s.height * 3
        self._queue = Queue(maxsize=maxsize)
        self._proc = Process(target=self._worker)

    @property
    def output(self) -> Queue:
        return self._queue

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type, value, traceback) -> None:
        pass

    def _worker(self) -> None:
        with open(self._input.output, 'rb') as pipe:
            while True:
                in_bytes = pipe.read(self._frame_size)
                if not in_bytes:
                    self._queue.put(None)
                    break
                frame = np.frombuffer(in_bytes, np.uint8).reshape(
                    (self._height, self._width, 3))
                self._queue.put(frame)

    def run(self) -> None:
        self._proc.start()

    def wait(self) -> None:
        self._proc.join()
