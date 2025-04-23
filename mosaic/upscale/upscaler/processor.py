import os
import queue
from pathlib import Path
from threading import Thread
from typing import Self

import numpy as np

from mosaic.upscale.filter import sharpen
from mosaic.upscale.net.real_esrgan import RealESRGANer
from mosaic.upscale.upscaler.splitter import Splitter


class Processor:
    _output_pipe = Path('/tmp/mosaic-upscale-processor-output')

    def __init__(self,
                 source: Splitter,
                 upsampler: RealESRGANer) -> None:
        self.origin = o = source.origin
        self._input = source
        self._height = o.height
        self._width = o.width
        self._frame_size = o.width * o.height * 3
        self._upsampler = upsampler
        self._reader_thread = Thread(target=self._reader_worker)
        self._processor_thread = Thread(target=self._processor_worker)
        self._writer_thread = Thread(target=self._writer_worker)
        self._reader_out_queue = queue.Queue[np.ndarray | None](maxsize=30)
        self._processor_out_queue = queue.Queue[np.ndarray | None](maxsize=30)

    @property
    def input(self) -> Path:
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

    def _reader_worker(self) -> None:
        with open(self.input, 'rb') as input:
            while True:
                # read from input pipe for bytes
                if not (in_bytes := input.read(self._frame_size)):
                    break

                # Convert bytes to numpy array
                shape = (self._height, self._width, 3)
                frame = np.frombuffer(in_bytes, np.uint8).reshape(shape)

                # write frame to out queue
                self._reader_out_queue.put(frame)

            # signal the end of frame stream
            self._reader_out_queue.put(None)

    def _processor_worker(self) -> None:
        while True:
            # get frame from reader out queue
            if (frame := self._reader_out_queue.get()) is None:
                break

            # apply a filter in python
            # TODO: do you upscaling magic here
            # frame = sharpen(frame)
            upscaled_frame, _ = self._upsampler.enhance(frame)

            # write frame to out queue
            self._processor_out_queue.put(upscaled_frame)

        # signal the end of frame stream
        self._processor_out_queue.put(None)

    def _writer_worker(self) -> None:
        with open(self.output, 'wb') as output:
            while True:
                # get frame from processor out queue
                if (frame := self._processor_out_queue.get()) is None:
                    break

                # write bytes to output
                out_bytes = frame.astype(np.uint8).tobytes()
                output.write(out_bytes)

    def run(self) -> None:
        self._reader_thread.start()
        self._processor_thread.start()
        self._writer_thread.start()

    def wait(self) -> None:
        self._reader_thread.join()
        self._processor_thread.join()
        self._writer_thread.join()
