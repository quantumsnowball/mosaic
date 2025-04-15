from pathlib import Path

import click

from mosaic.utils import HMS, HMSParamType, VideoPathParamType


@click.command()
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.option('-ss', '--start-time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end-time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.option('-y', '--force', is_flag=True, default=False, help='overwrite output file without asking')
@click.option('--time-tag', is_flag=True, default=False, help='auto append time tag at end of filename')
@click.argument('output-file', required=True, type=VideoPathParamType())
def free(
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    force: bool,
    time_tag: bool,
    output_file: Path,
) -> None:
    print(f'mosaic free -i {input_file} {output_file}')
