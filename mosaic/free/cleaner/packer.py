from multiprocessing import Process, Queue
from subprocess import Popen
from typing import Self

import numpy as np


class Packer:
    def __init__(self,
                 src: Popen,
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

    def _worker(self) -> None:
        if not self._src.stdout:
            return
        print('packer: I will start my worker loop')
        while True:
            in_bytes = self._src.stdout.read(self._frame_size)
            if not in_bytes:
                self._queue.put(None)
                break
            frame = np.frombuffer(in_bytes, np.uint8).reshape(
                (self._height, self._width, 3))
            self._queue.put(frame)
            # print('packer: I put a frame')

    @property
    def queue(self) -> Queue:
        return self._queue

    def run(self) -> Self:
        self._proc.start()
        return self

    def wait(self) -> None:
        self._proc.join()
