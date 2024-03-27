import os
from multiprocessing import Queue
from pathlib import Path
from threading import Thread

import cv2
import numpy as np
from alive_progress import alive_it
from numpy.typing import NDArray

from mosaic.free import utils
from mosaic.free.cleaner import runmodel
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.free.utils import filt
from mosaic.free.utils import image_processing as impro


def detect_mosaic_positions(netM: BiSeNet,
                            temp_dir: Path,
                            imagepaths: list[str],
                            savemask: bool = True,
                            medfilt_num: int = 11) -> NDArray:
    # resume
    continue_flag = False
    if os.path.isfile(os.path.join(temp_dir, 'step.json')):
        step = utils.loadjson(os.path.join(temp_dir, 'step.json'))
        resume_frame = int(step['frame'])
        if int(step['step']) > 2:
            pre_positions = np.load(os.path.join(temp_dir, 'mosaic_positions.npy'))
            return pre_positions
        if int(step['step']) >= 2 and resume_frame > 0:
            pre_positions = np.load(os.path.join(temp_dir, 'mosaic_positions.npy'))
            continue_flag = True
            imagepaths = imagepaths[resume_frame:]

    positions = []
    # t1 = time.time()

    img_read_pool = Queue(4)

    def loader(imagepaths: list[str]) -> None:
        for imagepath in imagepaths:
            img_origin = impro.imread(os.path.join(temp_dir/'video2image', imagepath))
            img_read_pool.put(img_origin)
    t = Thread(target=loader, args=(imagepaths,))
    t.setDaemon(True)
    t.start()

    for i, imagepath in enumerate(alive_it(imagepaths), 1):
        img_origin = img_read_pool.get()
        x, y, size, mask = runmodel.get_mosaic_position(img_origin, netM)
        positions.append([x, y, size])
        if savemask:
            t = Thread(target=cv2.imwrite, args=(str(temp_dir/'mosaic_mask'/imagepath), mask,))
            t.start()
        if i % 1000 == 0:
            save_positions = np.array(positions)
            if continue_flag:
                save_positions = np.concatenate((pre_positions, save_positions), axis=0)
            np.save(temp_dir / 'mosaic_positions.npy', save_positions)
            step = {'step': 2, 'frame': i+resume_frame}
            utils.savejson(temp_dir / 'step.json', step)

    print('\nOptimize mosaic locations...')
    positions = np.array(positions)
    if continue_flag:
        positions = np.concatenate((pre_positions, positions), axis=0)
    for i in range(3):
        positions[:, i] = filt.medfilt(positions[:, i], medfilt_num)
    step = {'step': 3, 'frame': 0}
    utils.savejson(temp_dir / 'step.json', step)
    np.save(temp_dir / 'mosaic_positions.npy', positions)

    return positions
