import os
import time
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Self

import cv2
import numpy as np
import torch

from mosaic.free.cleaner import runmodel
from mosaic.free.cleaner.packer import Package, Packer
from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.free_old.utils import data
from mosaic.free_old.utils import image_processing as impro

N, T, S = 2, 5, 3
LEFT_FRAME = (N*S)        # 6
POOL_NUM = LEFT_FRAME*2+1  # 13
INPUT_SIZE = 256
FRAME_POS = np.linspace(0, (T-1)*S, T, dtype=np.int64)


def remove_mosaic(x: int, y: int, size: int,
                  previous_frame: torch.Tensor | None,
                  *,
                  p: Package,
                  netG: BVDNet,
                  gpu_id: int = 0) -> tuple[torch.Tensor | None,
                                            np.ndarray,
                                            np.ndarray]:
    img_origin = p.img_origin
    img_pool = p.img_pool
    input_stream = []
    for pos in FRAME_POS:
        input_stream.append(impro.resize(
            img_pool[pos][y-size:y+size, x-size:x+size], INPUT_SIZE, interpolation=cv2.INTER_CUBIC)[:, :, ::-1])

    if previous_frame is None:
        previous_frame = data.im2tensor(
            input_stream[N], bgr2rgb=True, gpu_id=str(gpu_id))

    input_stream = np.array(input_stream).reshape(
        1, T, INPUT_SIZE, INPUT_SIZE, 3).transpose((0, 4, 1, 2, 3))
    input_stream = data.to_tensor(
        data.normalize(input_stream), gpu_id=gpu_id)

    with torch.no_grad():
        unmosaic_pred = netG(input_stream, previous_frame)

    img_fake = data.tensor2im(unmosaic_pred, rgb2bgr=True)
    previous_frame = unmosaic_pred

    return (previous_frame, img_origin.copy(), img_fake.copy())


class Processor:
    type InputItem = Package | None
    type Input = Queue[InputItem]

    _output_pipe = Path('/tmp/mosaic-free-processor-output')

    def __init__(self,
                 source: Packer,
                 *,
                 netM: BiSeNet,
                 netG: BVDNet,
                 min_mask_size: int = 50) -> None:
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

    def __enter__(self) -> Self:
        if not self.output.exists():
            os.mkfifo(self.output)
        return self

    def __exit__(self, type, value, traceback) -> None:
        if self.output.exists():
            self.output.unlink()

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
                x, y, size, mask = runmodel.get_mosaic_position(
                    package.img_origin, self._netM, all_mosaic_area=True)

                # if area is small skip to next frame
                if size < self._min_mask_size:
                    img_output = package.img_origin.copy()
                    out_bytes = img_output.astype(np.uint8).tobytes()
                    output.write(out_bytes)
                    continue

                # remove mosaic area
                previous_frame, img_origin, img_fake = remove_mosaic(
                    x, y, size, previous_frame, p=package, netG=self._netG)

                # replace with uncensored image
                img_output = impro.replace_mosaic(
                    img_origin, img_fake, mask, x, y, size, no_feather=False)

                # out_bytes = package.img_origin.astype(np.uint8).tobytes()
                out_bytes = img_output.astype(np.uint8).tobytes()

                output.write(out_bytes)

    def run(self) -> None:
        self._thread.start()

    def wait(self) -> None:
        self._thread.join()
