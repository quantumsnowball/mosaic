from typing import Any

import cv2
import numpy as np

from mosaic.free.cleaner.processor import utils
from mosaic.free.net.netM.BiSeNet import BiSeNet


def find_mostlikely_ROI(mask: np.ndarray) -> np.ndarray:
    contours, _hierarchy = cv2.findContours(
        mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        areas = []
        for contour in contours:
            areas.append(cv2.contourArea(contour))
        index = areas.index(max(areas))
        mask = np.zeros_like(mask)
        mask = cv2.fillPoly(mask, [contours[index]], (255))
    return mask


def boundingSquare(mask: np.ndarray,
                   Ex_mul: float) -> tuple[int, int, int, float]:
    # thresh = mask_threshold(mask,10,threshold)
    area = mask_area(mask)
    if area == 0:
        return 0, 0, 0, 0

    x, y, w, h = cv2.boundingRect(mask)

    center = np.array([int(x+w/2), int(y+h/2)])
    size = max(w, h)
    point0 = np.array([x, y])
    point1 = np.array([x+size, y+size])

    h, w = mask.shape[:2]
    if size*Ex_mul > min(h, w):
        size = min(h, w)
        halfsize = int(min(h, w)/2)
    else:
        size = Ex_mul*size
        halfsize = int(size/2)
        size = halfsize*2
    point0 = center - halfsize
    point1 = center + halfsize
    if point0[0] < 0:
        point0[0] = 0
        point1[0] = size
    if point0[1] < 0:
        point0[1] = 0
        point1[1] = size
    if point1[0] > w:
        point1[0] = w
        point0[0] = w-size
    if point1[1] > h:
        point1[1] = h
        point0[1] = h-size
    center = ((point0+point1)/2).astype('int')
    return center[0], center[1], halfsize, area


def mask_with_threshold(mask: np.ndarray,
                        ex_mun: int,
                        threshold: float) -> np.ndarray:
    mask = cv2.threshold(mask, threshold, 255, cv2.THRESH_BINARY)[1]
    mask = cv2.blur(mask, (ex_mun, ex_mun))
    mask = cv2.threshold(mask, threshold/5, 255, cv2.THRESH_BINARY)[1]
    return mask


def mask_area(mask: np.ndarray) -> float:
    mask = cv2.threshold(mask, 127, 255, 0)[1]
    # contours= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[1] #for opencv 3.4
    contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[
        0]  # updata to opencv 4.0
    try:
        area = cv2.contourArea(contours[0])
    except:
        area = 0
    return area


def run_segment(img: np.ndarray,
                netM: BiSeNet,
                size: int = 360,
                gpu_id: str = '-1') -> np.ndarray:
    img = utils.resize(img, size)
    img_tensor = utils.im2tensor(img, gpu_id=gpu_id, bgr2rgb=False, is0_1=True)
    mask = netM(img_tensor)
    mask = utils.tensor2im(mask, gray=True, is0_1=True)
    return mask


def get_mosaic_position(img_origin: np.ndarray,
                        netM: BiSeNet,
                        all_mosaic_area: bool = False,
                        mask_threshold: int = 64,
                        ex_mult: float = 1.5) -> tuple[int, int, int, Any]:
    h, w = img_origin.shape[:2]
    mask = run_segment(img_origin, netM, size=360, gpu_id='0')
    # mask_1 = mask.copy()
    mask = mask_with_threshold(mask,
                               ex_mun=int(min(h, w)/20),
                               threshold=mask_threshold)
    if not all_mosaic_area:
        mask = find_mostlikely_ROI(mask)
    x, y, size, _area = boundingSquare(mask, Ex_mul=ex_mult)
    # Location fix
    rat = min(h, w)/360.0
    x, y, size = int(rat*x), int(rat*y), int(rat*size)
    x, y = np.clip(x, 0, w), np.clip(y, 0, h)
    size = np.clip(size, 0, min(w-x, h-y))
    # print(x,y,size)
    return x, y, size, mask
