import sys
from typing import Any

import numpy as np

import mosaic.free.utils.image_processing as impro
from mosaic.free.utils import data

sys.path.append("..")


def run_segment(img, net, size=360, gpu_id='-1'):
    img = impro.resize(img, size)
    img = data.im2tensor(img, gpu_id=gpu_id, bgr2rgb=False, is0_1=True)
    mask = net(img)
    mask = data.tensor2im(mask, gray=True, is0_1=True)
    return mask


def get_mosaic_position(img_origin,
                        net_mosaic_pos,
                        all_mosaic_area: bool = False,
                        mask_threshold: int = 64,
                        ex_mult: float = 1.5) -> tuple[int, int, int, Any]:
    h, w = img_origin.shape[:2]
    mask = run_segment(img_origin, net_mosaic_pos, size=360, gpu_id='0')
    # mask_1 = mask.copy()
    mask = impro.mask_threshold(mask, ex_mun=int(
        min(h, w)/20), threshold=mask_threshold)
    if not all_mosaic_area:
        mask = impro.find_mostlikely_ROI(mask)
    x, y, size, area = impro.boundingSquare(mask, Ex_mul=ex_mult)
    # Location fix
    rat = min(h, w)/360.0
    x, y, size = int(rat*x), int(rat*y), int(rat*size)
    x, y = np.clip(x, 0, w), np.clip(y, 0, h)
    size = np.clip(size, 0, min(w-x, h-y))
    # print(x,y,size)
    return x, y, size, mask
