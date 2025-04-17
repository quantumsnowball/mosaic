import cv2
import numpy as np


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
