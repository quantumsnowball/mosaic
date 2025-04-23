import os
from pathlib import Path
from threading import Thread
from typing import Self

import numpy as np
import torch

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
        self._thread = Thread(target=self._worker)

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

    def _worker(self) -> None:
        with (
            open(self.input, 'rb') as input,
            open(self.output, 'wb') as output,
        ):
            while True:
                # read from input pipe for bytes
                in_bytes = input.read(self._frame_size)

                if not in_bytes:
                    break

                # Convert bytes to numpy array
                shape = (self._height, self._width, 3)
                frame = np.frombuffer(in_bytes, np.uint8).reshape(shape)

                # apply a filter in python
                # TODO: do you upscaling magic here
                # frame = sharpen(frame)
                upsampled_frame, _ = self._upsampler.enhance(frame)

                # write bytes to output
                out_bytes = upsampled_frame.astype(np.uint8).tobytes()
                output.write(out_bytes)

    def run(self) -> None:
        self._thread.start()

    def wait(self) -> None:
        self._thread.join()
