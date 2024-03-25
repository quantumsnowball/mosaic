from multiprocessing import Queue
from pathlib import Path

import click

from mosaic.free import utils
from mosaic.free.cleaner.clean import start_cleaner, start_result_writer
from mosaic.free.cleaner.extract import detect_mosaic_positions
from mosaic.free.cleaner.split import disassemble_video
from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.free.utils import ffmpeg
from mosaic.utils import HMS


def cleanmosaic_video_fusion(media_path: Path,
                             temp_dir: Path,
                             start_time: HMS | None,
                             end_time: HMS | None,
                             output_file: Path,
                             netG: BVDNet,
                             netM: BiSeNet) -> None:
    # prepare temp dirs
    utils.clean_tempfiles(temp_dir, True)

    # disassemble media into images and sound
    click.echo('Step:1/4 -- Convert video to images')
    fps, imagepaths, height, width = disassemble_video(temp_dir,
                                                       start_time,
                                                       end_time,
                                                       media_path)

    # detect mosaic in raw images
    click.echo('Step:2/4 -- Find mosaic location')
    start_frame = int(imagepaths[0][7:13])
    positions = detect_mosaic_positions(netM,
                                        temp_dir,
                                        imagepaths)[(start_frame-1):]

    # clean mosaic and save as images
    click.echo('Step:3/4 -- Clean Mosaic:')
    result_pool = Queue(4)
    writer_process = start_result_writer(result_pool, temp_dir)
    start_cleaner(result_pool, imagepaths, positions, temp_dir, netG)
    writer_process.join()
    result_pool.close()

    # re-assemble clean images into new video
    click.echo('Step:4/4 -- Convert images to video')
    ffmpeg.image2video(fps,
                       temp_dir/'replace_mosaic/output_%06d.jpg',
                       temp_dir/'voice_tmp.mp3',
                       output_file)

    # clean up temp dirs
    utils.clean_tempfiles(temp_dir, False)
