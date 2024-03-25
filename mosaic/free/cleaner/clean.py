import os
from multiprocessing import Process, Queue
from pathlib import Path
from threading import Thread

import cv2

from mosaic.free.utils import image_processing as impro


def start_result_writer(write_pool: Queue,
                        temp_dir: Path) -> Process:

    def worker() -> None:
        while True:
            # keep getting items from write_pool until None
            item = write_pool.get()
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
