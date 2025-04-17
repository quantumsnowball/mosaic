import time
from collections import deque
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Self

import numpy as np

from mosaic.free.cleaner.splitter import Splitter

N, T, S = 2, 5, 3
LEFT_FRAME = (N*S)        # 6
POOL_NUM = LEFT_FRAME*2+1  # 13


class Package:
    def __init__(self,
                 img_origin: np.ndarray,
                 img_pool: list[np.ndarray | None]) -> None:
        self.img_origin = img_origin
        self.img_pool = self._fillnone(img_pool)

    def _fillnone(self, l: list[np.ndarray | None]) -> list[np.ndarray]:
        # right pad
        for i in range(LEFT_FRAME, len(l)):
            if l[i] is None:
                l[i] = l[i-1]
        # left pad
        for i in range(-LEFT_FRAME-1, -len(l)-1, -1):
            if l[i] is None:
                l[i] = l[i+1]
        return l


class Packer:
    type OutputItem = Package | None
    type Output = Queue[OutputItem]

    def __init__(self,
                 source: Splitter,
                 *,
                 maxsize: int = 256) -> None:
        self.origin = o = source.origin
        self._input = source
        self._height = o.height
        self._width = o.width
        self._frame_size = o.width * o.height * 3
        self._queue = Queue(maxsize=maxsize)
        self._thread = Thread(target=self._worker)

    @property
    def input(self) -> Path:
        return self._input.output

    @property
    def output(self) -> Output:
        return self._queue

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type, value, traceback) -> None:
        pass

    def _worker(self) -> None:
        with open(self.input, 'rb') as input:
            buffer = deque[np.ndarray | None]([None,]*POOL_NUM,
                                              maxlen=POOL_NUM)
            while True:

                in_bytes = input.read(self._frame_size)
                if not in_bytes:
                    buffer.append(None)
                    print('not in_bytes')
                else:
                    shape = (self._height, self._width, 3)
                    frame = np.frombuffer(in_bytes, np.uint8).reshape(shape)
                    buffer.append(frame)
                img_pool = list(buffer)

                img_origin = img_pool[LEFT_FRAME]

                if img_origin is not None:
                    self.output.put(Package(img_origin, img_pool))

                if all(val is None for val in img_pool[LEFT_FRAME:]):
                    break

            # signal the end of Output queue
            self.output.put(None)

    def run(self) -> None:
        self._thread.start()

    def wait(self) -> None:
        self._thread.join()
