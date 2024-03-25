import os
import time
from multiprocessing import Queue
from pathlib import Path
from threading import Thread

import cv2
import numpy as np
import torch

from mosaic.free import utils
from mosaic.free.cleaner.extract import detect_mosaic_positions
from mosaic.free.cleaner.split import disassemble_video
from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.free.utils import data, ffmpeg
from mosaic.free.utils import image_processing as impro
from mosaic.utils import HMS


def cleanmosaic_video_fusion(media_path: Path,
                             temp_dir: Path,
                             start_time: HMS | None,
                             end_time: HMS | None,
                             output_file: Path,
                             netG: BVDNet,
                             netM: BiSeNet,
                             gpu_id: int = 0) -> None:
    path = media_path
    N, T, S = 2, 5, 3
    LEFT_FRAME = (N*S)
    POOL_NUM = LEFT_FRAME*2+1
    INPUT_SIZE = 256
    FRAME_POS = np.linspace(0, (T-1)*S, T, dtype=np.int64)
    img_pool = []
    previous_frame = None
    init_flag = True

    utils.clean_tempfiles(temp_dir, True)

    fps, imagepaths, height, width = disassemble_video(temp_dir,
                                                       start_time,
                                                       end_time,
                                                       path)
    start_frame = int(imagepaths[0][7:13])
    positions = detect_mosaic_positions(netM,
                                        temp_dir,
                                        imagepaths)[(start_frame-1):]
    t1 = time.time()

    # clean mosaic
    print('Step:3/4 -- Clean Mosaic:')
    length = len(imagepaths)
    write_pool = Queue(4)

    def write_result(no_feather: bool = False) -> None:
        while True:
            try:
                item = write_pool.get()
            except ValueError:
                break
            save_ori, imagepath, img_origin, img_fake, x, y, size = item
            if save_ori:
                img_result = img_origin
            else:
                mask = cv2.imread(str(temp_dir/'mosaic_mask' / imagepath), 0)
                img_result = impro.replace_mosaic(img_origin, img_fake, mask, x, y, size, no_feather)
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
        print('\r', str(i+1)+'/'+str(length), utils.get_bar(100*i/length, num=35),
              utils.counttime(t1, t2, i+1, len(imagepaths)), end='')
    print()

    write_pool.close()

    print('Step:4/4 -- Convert images to video')
    ffmpeg.image2video(fps,
                       temp_dir/'replace_mosaic/output_%06d.jpg',
                       temp_dir/'voice_tmp.mp3',
                       output_file)

    utils.clean_tempfiles(temp_dir, False)
