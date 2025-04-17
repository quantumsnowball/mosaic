import platform

import cv2
import numpy as np

system_type = 'Linux'
if 'Windows' in platform.platform():
    system_type = 'Windows'


def resize(img, size, interpolation=cv2.INTER_LINEAR):
    '''
    cv2.INTER_NEAREST      最邻近插值点法
    cv2.INTER_LINEAR        双线性插值法
    cv2.INTER_AREA         邻域像素再取样插补
    cv2.INTER_CUBIC        双立方插补，4*4大小的补点
    cv2.INTER_LANCZOS4     8x8像素邻域的Lanczos插值
    '''
    h, w = img.shape[:2]
    if np.min((w, h)) == size:
        return img
    if w >= h:
        res = cv2.resize(img, (int(size*w/h), size),
                         interpolation=interpolation)
    else:
        res = cv2.resize(img, (size, int(size*h/w)),
                         interpolation=interpolation)
    return res


def find_mostlikely_ROI(mask):
    contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        areas = []
        for contour in contours:
            areas.append(cv2.contourArea(contour))
        index = areas.index(max(areas))
        mask = np.zeros_like(mask)
        mask = cv2.fillPoly(mask, [contours[index]], (255))
    return mask


def boundingSquare(mask, Ex_mul):
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


def mask_threshold(mask, ex_mun, threshold):
    mask = cv2.threshold(mask, threshold, 255, cv2.THRESH_BINARY)[1]
    mask = cv2.blur(mask, (ex_mun, ex_mun))
    mask = cv2.threshold(mask, threshold/5, 255, cv2.THRESH_BINARY)[1]
    return mask


def mask_area(mask):
    mask = cv2.threshold(mask, 127, 255, 0)[1]
    # contours= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[1] #for opencv 3.4
    contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[
        0]  # updata to opencv 4.0
    try:
        area = cv2.contourArea(contours[0])
    except:
        area = 0
    return area
