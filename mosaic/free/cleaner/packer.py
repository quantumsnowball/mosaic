from multiprocessing import Process, Queue
from typing import Self

import numpy as np

from mosaic.free.cleaner.splitter import Splitter


class Packer:
    def __init__(self,
                 src: Splitter,
                 *,
                 height: int,
                 width: int,
                 maxsize: int = 1) -> None:
        self._src = src
        self._height = height
        self._width = width
        self._frame_size = width * height * 3
        self._queue = Queue(maxsize=maxsize)
        self._proc = Process(target=self._worker)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type, value, traceback) -> None:
        pass

    def _worker(self) -> None:
        with open(self._src.output_pipe, 'rb') as pipe:
            while True:
                in_bytes = pipe.read(self._frame_size)
                if not in_bytes:
                    self._queue.put(None)
                    break
                frame = np.frombuffer(in_bytes, np.uint8).reshape(
                    (self._height, self._width, 3))
                self._queue.put(frame)

    @property
    def queue(self) -> Queue:
        return self._queue

    def run(self) -> None:
        self._proc.start()

    def wait(self) -> None:
        self._proc.join()
