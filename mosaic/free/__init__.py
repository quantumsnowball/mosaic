from pathlib import Path

import click

import mosaic.free.args as args
from mosaic.free.cleaner import Cleaner
from mosaic.free.net.netG import video
from mosaic.free.net.netM import bisenet
from mosaic.utils.logging import log
from mosaic.utils.path import PathParamType
from mosaic.utils.service import service
from mosaic.utils.time import HMS, HMSParamType

PACKAGE_DIR = Path(__file__).parent


@click.command()
@click.option('-i', '--input-file', required=True, type=PathParamType(), help='input media path')
@click.option('-ss', '--start-time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end-time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.option('-y', '--force', is_flag=True, default=False, help='overwrite output file without asking')
@click.option('--time-tag', is_flag=True, default=False, help='auto append time tag at end of filename')
@click.option('--raw-info', is_flag=True, default=False, help='display raw ffmpeg info')
@click.argument('output-file', required=True, type=PathParamType())
@service()
@args.preprocess
def free(
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    raw_info: bool,
    output_file: Path,
) -> None:
    # run
    with Cleaner(
        input_file=input_file,
        start_time=start_time,
        end_time=end_time,
        output_file=output_file,
        raw_info=raw_info,
        netM=bisenet(PACKAGE_DIR/'net/netM/state_dicts/mosaic_position.pth'),
        netG=video(PACKAGE_DIR/'net/netG/state_dicts/clean_youknow_video.pth'),
    ) as cleaner:
        try:
            cleaner.run()
        except KeyboardInterrupt as e:
            log.info(e.__class__)
            cleaner.stop()
