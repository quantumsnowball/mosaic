from pathlib import Path

import click

import mosaic.lada.args as args
from mosaic.lada.cleaner import Cleaner
from mosaic.utils.logging import log
from mosaic.utils.path import PathParamType
from mosaic.utils.service import service
from mosaic.utils.time import HMS, HMSParamType

PACKAGE_DIR = Path(__file__).parent


@click.command()
@service()
@click.option('-i', '--input-file', required=True, type=PathParamType(), help='input media path')
@click.option('-ss', '--start-time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end-time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.option('-y', '--force', is_flag=True, default=False, help='overwrite output file without asking')
@click.option('--time-tag', is_flag=True, default=False, help='auto append time tag at end of filename')
@click.option('--raw-info', is_flag=True, default=False, help='display raw ffmpeg info')
@click.argument('output-file', required=True, type=PathParamType())
@args.preprocess
def lada(
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
        netD_path=PACKAGE_DIR / 'net/state_dicts/lada_mosaic_detection_model_v2.pt',
        netR_path=PACKAGE_DIR / 'net/state_dicts/lada_mosaic_restoration_model_generic_v1.2.pth',
    ) as cleaner:
        try:
            cleaner.run()
        except KeyboardInterrupt as e:
            log.info(e.__class__)
            cleaner.stop()
