import multiprocessing as mp
import os
import queue
import uuid
from dataclasses import dataclass
from pathlib import Path
from queue import ShutDown
from threading import Thread
from typing import Self

import numpy as np

from mosaic.upscale.net.real_esrgan import RealESRGANer
from mosaic.upscale.upscaler.splitter import Splitter
from mosaic.utils import TEMP_DIR
from mosaic.utils.exception import catch
from mosaic.utils.logging import log


@dataclass
class UpsampleInfo:
    width: int
    height: int
    channel: int
    mode: str

    @property
    def s(self) -> str:
        return f'{self.width}x{self.height}'

    @property
    def pix_fmt(self) -> str:
        # TODO: which output format should I use?
        return 'yuv420p'


class Processor:
    _queue_size = 1

    def __init__(self,
                 source: Splitter,
                 upsampler: RealESRGANer) -> None:
        self._output_pipe = TEMP_DIR / f'{__name__}.{uuid.uuid4()}'
        self.origin = o = source.origin
        self._input = source
        self._height = o.height
        self._width = o.width
        self._frame_size = o.width * o.height * 3
        self._upsampler = upsampler

        # worker threads
        self._reader_thread = Thread(target=self._reader_worker)
        self._processor_thread = Thread(target=self._processor_worker)
        self._writer_thread = Thread(target=self._writer_worker)

        # queues
        # (2nd queue is slightly bigger to prevent queue full blocking)
        self._reader_out_queue = queue.Queue[np.ndarray | None](maxsize=self._queue_size)
        self._processor_out_queue = queue.Queue[np.ndarray | None](maxsize=self._queue_size+2)
        self._upsampled_info: 'mp.Queue[UpsampleInfo]' = mp.Queue(maxsize=1)

    @property
    def input(self) -> Path:
        return self._input.output

    @property
    def output(self) -> Path:
        return self._output_pipe

    @property
    def upsampled_info(self) -> 'mp.Queue[UpsampleInfo]':
        return self._upsampled_info

    @log.info
    def __enter__(self) -> Self:
        if not self.output.exists():
            os.mkfifo(self.output)
        return self

    @log.info
    def __exit__(self, type, value, traceback) -> None:
        if self.output.exists():
            self.output.unlink()

    @log.info
    @catch(ShutDown, ValueError)
    def _reader_worker(self) -> None:
        with open(self.input, 'rb') as input:
            while True:
                # read from input pipe for bytes
                if not (in_bytes := input.read(self._frame_size)):
                    break

                # Convert bytes to numpy array, break on incomplete frame raises ValueError
                shape = (self._height, self._width, 3)
                frame = np.frombuffer(in_bytes, np.uint8).reshape(shape)

                # write frame to out queue
                self._reader_out_queue.put(frame)

            # signal the end of frame stream
            self._reader_out_queue.put(None)

    @log.info
    @catch(ShutDown, ValueError)
    def _processor_worker(self) -> None:
        info_known = False
        while True:
            # get frame from reader out queue
            if (original_frame := self._reader_out_queue.get()) is None:
                break

            # apply a filter in python
            frame, mode = self._upsampler.enhance(original_frame)

            # determine upsampled frame info
            if not info_known:
                height, width, channel = frame.shape
                self._upsampled_info.put(UpsampleInfo(width, height, channel, mode))
                info_known = True

            # write frame to out queue
            self._processor_out_queue.put(frame)

        # signal the end of frame stream
        self._processor_out_queue.put(None)

    @log.info
    @catch(ShutDown, BrokenPipeError)
    def _writer_worker(self) -> None:
        with open(self.output, 'wb') as output:
            while True:
                # get frame from processor out queue
                if (frame := self._processor_out_queue.get()) is None:
                    break

                # write bytes to output
                out_bytes = frame.astype(np.uint8).tobytes()
                output.write(out_bytes)

    @log.info
    def run(self) -> None:
        self._reader_thread.start()
        self._processor_thread.start()
        self._writer_thread.start()

    @log.info
    def wait(self) -> None:
        if self._reader_thread.is_alive():
            self._reader_thread.join()
        if self._processor_thread.is_alive():
            self._processor_thread.join()
        if self._writer_thread.is_alive():
            self._writer_thread.join()

    @log.info
    def stop(self) -> None:
        # raises ShutDown
        self._reader_out_queue.shutdown(immediate=True)
        self._processor_out_queue.shutdown(immediate=True)
        # raises ValueError
        self._upsampled_info.close()
        # raises BrokenPipeError
        if self.output.exists():
            self.output.unlink()
