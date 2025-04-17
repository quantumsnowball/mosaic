import cv2
import numpy as np
import torch

from mosaic.free.cleaner.constants import FRAME_POS, INPUT_SIZE, N, T
from mosaic.free.cleaner.packer import Package
from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.utils import data
from mosaic.free.utils import image_processing as impro


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
