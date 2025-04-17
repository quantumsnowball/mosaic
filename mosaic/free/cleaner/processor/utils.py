import cv2
import numpy as np
import torch


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


def tensor2im(image_tensor, gray=False, rgb2bgr=True, is0_1=False, batch_index=0):
    image_tensor = image_tensor.data
    image_numpy = image_tensor[batch_index].cpu().float().numpy()

    if not is0_1:
        image_numpy = (image_numpy + 1)/2.0
    image_numpy = np.clip(image_numpy * 255.0, 0, 255)

    # gray -> output 1ch
    if gray:
        h, w = image_numpy.shape[1:]
        image_numpy = image_numpy.reshape(h, w)
        return image_numpy.astype(np.uint8)

    # output 3ch
    if image_numpy.shape[0] == 1:
        image_numpy = np.tile(image_numpy, (3, 1, 1))
    image_numpy = image_numpy.transpose((1, 2, 0))
    if rgb2bgr and not gray:
        image_numpy = image_numpy[..., ::-1]-np.zeros_like(image_numpy)
    return image_numpy.astype(np.uint8)


def im2tensor(image_numpy, gray=False, bgr2rgb=True, reshape=True, gpu_id='-1', is0_1=False):
    if gray:
        h, w = image_numpy.shape
        image_numpy = (image_numpy/255.0-0.5)/0.5
        image_tensor = torch.from_numpy(image_numpy).float()
        if reshape:
            image_tensor = image_tensor.reshape(1, 1, h, w)
    else:
        h, w, ch = image_numpy.shape
        if bgr2rgb:
            image_numpy = image_numpy[..., ::-1]-np.zeros_like(image_numpy)
        if is0_1:
            image_numpy = image_numpy/255.0
        else:
            image_numpy = (image_numpy/255.0-0.5)/0.5
        image_numpy = image_numpy.transpose((2, 0, 1))
        image_tensor = torch.from_numpy(image_numpy).float()
        if reshape:
            image_tensor = image_tensor.reshape(1, ch, h, w)
    if gpu_id != '-1':
        image_tensor = image_tensor.cuda()
    return image_tensor
