from pathlib import Path

import click

from mosaic.utils.path import PathParamType
from mosaic.utils.service import service
from mosaic.utils.time import HMS, HMSParamType


@click.command()
@service()
@click.option('-i', '--input-file', required=True, type=PathParamType(), help='input media path')
@click.option('-ss', '--start-time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end-time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
# @click.option('-y', '--force', is_flag=True, default=False, help='overwrite output file without asking')
# @click.option('--time-tag', is_flag=True, default=False, help='auto append time tag at end of filename')
@click.option('--raw-info', is_flag=True, default=False, help='display raw ffmpeg info')
@click.argument('output-file', required=True, type=PathParamType())
def lada(
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    raw_info: bool,
    output_file: Path,
) -> None:
    # run
    print(f'{start_time=} {end_time=} {raw_info=} {input_file=} {output_file=}')
