from collections import deque
from pathlib import Path
from queue import Queue, ShutDown
from threading import Thread
from typing import Self, cast

import numpy as np

from mosaic.free.cleaner.constants import LEFT_FRAME, POOL_NUM
from mosaic.free.cleaner.splitter import Splitter
from mosaic.utils.exception import catch
from mosaic.utils.logging import log


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
        # the list should be None value free by now
        filled = cast(list[np.ndarray], l)
        return filled


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

    @log.info
    def __enter__(self) -> Self:
        return self

    @log.info
    def __exit__(self, type, value, traceback) -> None:
        pass

    @log.info
    @catch(ShutDown)
    def _worker(self) -> None:
        with open(self.input, 'rb') as input:
            # buffer is first prefilled with None values
            # then auto shift when appending and create a sliding window
            buffer = deque[np.ndarray | None]([None,]*POOL_NUM,
                                              maxlen=POOL_NUM)
            while True:
                # read from input pipe for a frame
                in_bytes = input.read(self._frame_size)
                if in_bytes and len(in_bytes) == self._frame_size:
                    shape = (self._height, self._width, 3)
                    frame = np.frombuffer(in_bytes, np.uint8).reshape(shape)
                    buffer.append(frame)
                else:
                    buffer.append(None)

                # img_pool is the current window
                img_pool = list(buffer)
                # img_origin is the buffer center item
                img_origin = img_pool[LEFT_FRAME]

                # when the center img_origin exists, it is a valid window
                # on queue shutdown, ShutDown is raised and break the loop
                if img_origin is not None:
                    # hand it to Package and put to output queue
                    self.output.put(Package(img_origin, img_pool))
                # else, it can only be the starting or ending stage
                elif all(val is None for val in img_pool[LEFT_FRAME:]):
                    # when center to right all items are None, sliding window has ended
                    # can only be after the ending stage, signal the end of Output queue
                    self.output.put(None)
                    # also time to break the loop
                    break

    @log.info
    def run(self) -> None:
        self._thread.start()

    @log.info
    def wait(self) -> None:
        if self._thread.is_alive():
            self._thread.join()

    @log.info
    def stop(self) -> None:
        # raises ShutDown
        self.output.shutdown(immediate=True)
