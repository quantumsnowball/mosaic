import cv2
import numpy as np


def ch_one2three(img):
    res = cv2.merge([img, img, img])
    return res


def replace_mosaic(img_origin: np.ndarray,
                   img_fake: np.ndarray,
                   mask: np.ndarray,
                   x: int,
                   y: int,
                   size: int,
                   no_feather: bool):
    img_fake = cv2.resize(img_fake, (size*2, size*2),
                          interpolation=cv2.INTER_CUBIC)
    if no_feather:
        img_origin[y-size:y+size, x-size:x+size] = img_fake
        return img_origin
    else:
        # #color correction
        # RGB_origin = img_origin[y-size:y+size,x-size:x+size].mean(0).mean(0)
        # RGB_fake = img_fake.mean(0).mean(0)
        # for i in range(3):img_fake[:,:,i] = np.clip(img_fake[:,:,i]+RGB_origin[i]-RGB_fake[i],0,255)
        # eclosion
        eclosion_num = int(size/10)+2
        mask_crop = cv2.resize(mask, (img_origin.shape[1], img_origin.shape[0]))[
            y-size:y+size, x-size:x+size]
        mask_crop = ch_one2three(mask_crop)

        mask_crop = (cv2.blur(mask_crop, (eclosion_num, eclosion_num)))
        mask_crop = mask_crop/255.0

        img_crop = img_origin[y-size:y+size, x-size:x+size]
        img_origin[y-size:y+size, x-size:x +
                   size] = np.clip((img_crop*(1-mask_crop)+img_fake*mask_crop), 0, 255).astype('uint8')

        return img_origin
