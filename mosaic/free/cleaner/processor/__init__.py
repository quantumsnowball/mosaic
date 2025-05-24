import os
import uuid
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Self

import numpy as np

from mosaic.free.cleaner.packer import Package, Packer
from mosaic.free.cleaner.processor.position import get_mosaic_position
from mosaic.free.cleaner.processor.remove import remove_mosaic
from mosaic.free.cleaner.processor.replace import replace_mosaic
from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.utils import TEMP_DIR
from mosaic.utils.logging import log


class Processor:
    type InputItem = Package | None
    type Input = Queue[InputItem]

    def __init__(self,
                 source: Packer,
                 *,
                 netM: BiSeNet,
                 netG: BVDNet,
                 min_mask_size: int = 50) -> None:
        self._output_pipe = TEMP_DIR / f'{__name__}.{uuid.uuid4()}'
        self.origin = source.origin
        self._input = source
        self._netM = netM
        self._netG = netG
        self._min_mask_size = min_mask_size
        self._thread = Thread(target=self._worker)

    @property
    def input(self) -> Input:
        return self._input.output

    @property
    def output(self) -> Path:
        return self._output_pipe

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
    def _worker(self) -> None:
        with open(self.output, 'wb') as output:
            previous_frame = None
            while True:
                # read a frame package from input queue
                package = self.input.get()

                # if no more further data, quit loop
                if package is None:
                    break

                # detect mosaic position
                x, y, size, mask = get_mosaic_position(
                    package.img_origin, self._netM, all_mosaic_area=True)

                # if area is small skip to next frame
                if size < self._min_mask_size:
                    img_output = package.img_origin.copy()
                    out_bytes = img_output.astype(np.uint8).tobytes()
                    try:
                        output.write(out_bytes)
                    except BrokenPipeError:
                        break
                    continue

                # remove mosaic area
                previous_frame, img_origin, img_fake = remove_mosaic(
                    x, y, size, previous_frame, p=package, netG=self._netG)

                # replace with uncensored image
                img_output = replace_mosaic(
                    img_origin, img_fake, mask, x, y, size, no_feather=False)

                # write bytes to output
                out_bytes = img_output.astype(np.uint8).tobytes()
                try:
                    output.write(out_bytes)
                except BrokenPipeError:
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
        if self.output.exists():
            self.output.unlink()
