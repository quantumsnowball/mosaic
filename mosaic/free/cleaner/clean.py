import os
from multiprocessing import Process, Queue
from pathlib import Path

import cv2
import numpy as np
import torch
from alive_progress import alive_it
from numpy.typing import NDArray

from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.utils import data
from mosaic.free.utils import image_processing as impro


def start_result_writer(result_pool: Queue,
                        temp_dir: Path) -> Process:

    def worker() -> None:
        while True:
            # keep getting items from write_pool until None
            item = result_pool.get()
            if item is None:
                break
            save_ori, imagepath, img_origin, img_fake, x, y, size = item

            # process image with mask
            if save_ori:
                img_result = img_origin
            else:
                mask = cv2.imread(str(temp_dir/'mosaic_mask' / imagepath), 0)
                img_result = impro.replace_mosaic(img_origin, img_fake, mask, x, y, size, no_feather=False)

            # save result to temp dir
            cv2.imwrite(str(temp_dir/'replace_mosaic' / imagepath), img_result)

            # remove original image
            os.remove(temp_dir/'video2image' / imagepath)

    # run worker in a new process
    p = Process(target=worker, args=())
    p.start()

    # return thread
    return p


def start_cleaner(result_pool: Queue,
                  imagepaths: list[str],
                  positions: NDArray,
                  temp_dir: Path,
                  netG: BVDNet,
                  gpu_id: int = 0) -> None:
    N, T, S = 2, 5, 3
    LEFT_FRAME = (N*S)
    POOL_NUM = LEFT_FRAME*2+1
    INPUT_SIZE = 256
    FRAME_POS = np.linspace(0, (T-1)*S, T, dtype=np.int64)
    img_pool = []
    previous_frame = None
    init_flag = True

    # t1 = time.time()

    for i, imagepath in enumerate(alive_it(imagepaths), 0):
        x, y, size = positions[i][0], positions[i][1], positions[i][2]
        input_stream = []
        # image read stream
        if i == 0:  # init
            for j in range(POOL_NUM):
                img_pool.append(impro.imread(os.path.join(str(temp_dir)+'/video2image',
                                imagepaths[np.clip(i+j-LEFT_FRAME, 0, len(imagepaths)-1)])))
        else:  # load next frame
            img_pool.pop(0)
            img_pool.append(impro.imread(os.path.join(str(temp_dir)+'/video2image',
                            imagepaths[np.clip(i+LEFT_FRAME, 0, len(imagepaths)-1)])))
        img_origin = img_pool[LEFT_FRAME]

        if size > 50:
            try:  # Avoid unknown errors
                for pos in FRAME_POS:
                    input_stream.append(impro.resize(
                        img_pool[pos][y-size:y+size, x-size:x+size], INPUT_SIZE, interpolation=cv2.INTER_CUBIC)[:, :, ::-1])
                if init_flag:
                    init_flag = False
                    previous_frame = input_stream[N]
                    previous_frame = data.im2tensor(previous_frame, bgr2rgb=True, gpu_id=str(gpu_id))

                input_stream = np.array(input_stream).reshape(
                    1, T, INPUT_SIZE, INPUT_SIZE, 3).transpose((0, 4, 1, 2, 3))
                input_stream = data.to_tensor(data.normalize(input_stream), gpu_id=gpu_id)
                with torch.no_grad():
                    unmosaic_pred = netG(input_stream, previous_frame)
                img_fake = data.tensor2im(unmosaic_pred, rgb2bgr=True)
                previous_frame = unmosaic_pred
                result_pool.put([False, imagepath, img_origin.copy(), img_fake.copy(), x, y, size])
            except Exception as e:
                init_flag = True
                print('Error:', e)
        else:
            result_pool.put([True, imagepath, img_origin.copy(), -1, -1, -1, -1])
            init_flag = True

    print()

    # indicate no more result to be put into pool
    result_pool.put(None)
