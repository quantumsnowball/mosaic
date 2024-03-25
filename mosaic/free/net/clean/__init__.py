import os
import time
from multiprocessing import Process, Queue
from pathlib import Path
from threading import Thread
from typing import Any

import cv2
import numpy as np
import torch

# from models import runmodel
from mosaic.free.net.clean import runmodel
from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.free.net.util import data, ffmpeg, filt
from mosaic.free.net.util import image_processing as impro
from mosaic.free.net.util import util

# from .init import video_init


def video_init(temp_dir: Path,
               result_dir: Path,
               start_time,
               last_time,
               path: Path) -> tuple[Any, list[str], int, int]:
    fps, endtime, height, width = ffmpeg.get_video_infos(path)

    print('Step:1/4 -- Convert video to images')
    # util.file_init(result_dir)

    ffmpeg.video2voice(path,
                       temp_dir/'voice_tmp.mp3',
                       start_time,
                       last_time)
    ffmpeg.video2image(path,
                       temp_dir/'video2image/output_%06d.jpg',
                       fps,
                       start_time,
                       last_time)
    imagepaths = os.listdir(temp_dir/'video2image')
    imagepaths.sort()
    step = {'step': 2, 'frame': 0}
    util.savejson(temp_dir/'step.json', step)

    return fps, imagepaths, height, width


'''
---------------------Clean Mosaic---------------------
'''


def get_mosaic_positions(netM: BiSeNet,
                         temp_dir: Path,
                         imagepaths: list[str],
                         savemask: bool = True,
                         medfilt_num: int = 11,
                         no_preview: bool = True):
    # resume
    continue_flag = False
    if os.path.isfile(os.path.join(temp_dir, 'step.json')):
        step = util.loadjson(os.path.join(temp_dir, 'step.json'))
        resume_frame = int(step['frame'])
        if int(step['step']) > 2:
            pre_positions = np.load(os.path.join(temp_dir, 'mosaic_positions.npy'))
            return pre_positions
        if int(step['step']) >= 2 and resume_frame > 0:
            pre_positions = np.load(os.path.join(temp_dir, 'mosaic_positions.npy'))
            continue_flag = True
            imagepaths = imagepaths[resume_frame:]

    positions = []
    t1 = time.time()
    if not no_preview:
        cv2.namedWindow('mosaic mask', cv2.WINDOW_NORMAL)
    print('Step:2/4 -- Find mosaic location')

    img_read_pool = Queue(4)

    def loader(imagepaths: list[str]):
        for imagepath in imagepaths:
            img_origin = impro.imread(os.path.join(temp_dir/'video2image', imagepath))
            img_read_pool.put(img_origin)
    t = Thread(target=loader, args=(imagepaths,))
    t.setDaemon(True)
    t.start()

    for i, imagepath in enumerate(imagepaths, 1):
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
            util.savejson(temp_dir / 'step.json', step)

        # preview result and print
        if not no_preview:
            cv2.imshow('mosaic mask', mask)
            cv2.waitKey(1) & 0xFF
        t2 = time.time()
        print('\r', str(i)+'/'+str(len(imagepaths)), util.get_bar(100*i/len(imagepaths), num=35),
              util.counttime(t1, t2, i, len(imagepaths)), end='')

    if not no_preview:
        cv2.destroyAllWindows()
    print('\nOptimize mosaic locations...')
    positions = np.array(positions)
    if continue_flag:
        positions = np.concatenate((pre_positions, positions), axis=0)
    for i in range(3):
        positions[:, i] = filt.medfilt(positions[:, i], medfilt_num)
    step = {'step': 3, 'frame': 0}
    util.savejson(temp_dir / 'step.json', step)
    np.save(temp_dir / 'mosaic_positions.npy', positions)

    return positions


def cleanmosaic_video_fusion(media_path: Path,
                             temp_dir: Path,
                             result_dir: Path,
                             start_time,
                             end_time,
                             output_file: Path,
                             netG: BVDNet,
                             netM: BiSeNet,
                             no_preview: bool = True,
                             gpu_id: int = 0):
    path = media_path
    N, T, S = 2, 5, 3
    LEFT_FRAME = (N*S)
    POOL_NUM = LEFT_FRAME*2+1
    INPUT_SIZE = 256
    FRAME_POS = np.linspace(0, (T-1)*S, T, dtype=np.int64)
    img_pool = []
    previous_frame = None
    init_flag = True

    util.clean_tempfiles(temp_dir, True)

    fps, imagepaths, height, width = video_init(temp_dir,
                                                result_dir,
                                                start_time,
                                                end_time,
                                                path)
    start_frame = int(imagepaths[0][7:13])
    positions = get_mosaic_positions(netM,
                                     temp_dir,
                                     imagepaths)[(start_frame-1):]
    t1 = time.time()
    if not no_preview:
        cv2.namedWindow('clean', cv2.WINDOW_NORMAL)

    # clean mosaic
    print('Step:3/4 -- Clean Mosaic:')
    length = len(imagepaths)
    write_pool = Queue(4)
    show_pool = Queue(4)

    def write_result(no_feather: bool = False):
        while True:
            save_ori, imagepath, img_origin, img_fake, x, y, size = write_pool.get()
            if save_ori:
                img_result = img_origin
            else:
                mask = cv2.imread(str(temp_dir/'mosaic_mask' / imagepath), 0)
                img_result = impro.replace_mosaic(img_origin, img_fake, mask, x, y, size, no_feather)
            if not no_preview:
                show_pool.put(img_result.copy())
            cv2.imwrite(str(temp_dir/'replace_mosaic' / imagepath), img_result)
            os.remove(temp_dir/'video2image' / imagepath)
    t = Thread(target=write_result, args=())
    t.setDaemon(True)
    t.start()

    for i, imagepath in enumerate(imagepaths, 0):
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

        # preview result and print
        if not no_preview:
            if show_pool.qsize() > 3:
                cv2.imshow('clean', show_pool.get())
                cv2.waitKey(1) & 0xFF

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
                write_pool.put([False, imagepath, img_origin.copy(), img_fake.copy(), x, y, size])
            except Exception as e:
                init_flag = True
                print('Error:', e)
        else:
            write_pool.put([True, imagepath, img_origin.copy(), -1, -1, -1, -1])
            init_flag = True

        t2 = time.time()
        print('\r', str(i+1)+'/'+str(length), util.get_bar(100*i/length, num=35),
              util.counttime(t1, t2, i+1, len(imagepaths)), end='')
    print()
    write_pool.close()
    show_pool.close()
    if not no_preview:
        cv2.destroyAllWindows()
    print('Step:4/4 -- Convert images to video')
    ffmpeg.image2video(fps,
                       temp_dir/'replace_mosaic/output_%06d.jpg',
                       temp_dir/'voice_tmp.mp3',
                       output_file)
