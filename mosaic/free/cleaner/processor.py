from multiprocessing import Process, Queue
from subprocess import Popen
from typing import Self

import numpy as np


class Processor:
    def __init__(self,
                 src: Queue,
                 dst: Popen) -> None:
        self._src = src
        self._dst = dst
        self._proc = Process(target=self._worker)

    def _worker(self) -> None:
        if not self._dst.stdin:
            return
        print('processor: I will start my worker loop')
        while True:
            frame = self._src.get()
            if frame is None:
                break
            out_bytes = frame.astype(np.uint8).tobytes()
            self._dst.stdin.write(out_bytes)
            # print('processor: I got a frame')

    def run(self) -> Self:
        self._proc.start()
        return self

    def wait(self) -> None:
        self._proc.join()
