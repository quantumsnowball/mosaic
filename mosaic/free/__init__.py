from pathlib import Path

import click

import mosaic.free.cleaner as cleaner
from mosaic.free.net.netG import video
from mosaic.free.net.netM import bisenet
from mosaic.utils import HMS, HMSParamType, VideoPathParamType

PACKAGE_DIR = Path(__file__).parent


@click.command()
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.option('-ss', '--start-time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end-time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.option('-y', '--force', is_flag=True, default=False, help='overwrite output file without asking')
@click.option('--time-tag', is_flag=True, default=False, help='auto append time tag at end of filename')
@click.option('--raw-info', is_flag=True, default=False, help='display raw ffmpeg info')
@click.argument('output-file', required=True, type=VideoPathParamType())
def free(
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    force: bool,
    time_tag: bool,
    raw_info: bool,
    output_file: Path,
) -> None:
    # verify inputs
    assert input_file.exists(), f'{input_file} does not exists'
    if start_time and end_time:
        if not end_time > start_time:
            raise ValueError('Invalid start time or end time')
    if not force and output_file.exists():
        if input(f'Output file {output_file} already exist, overwrite? y/[N] ').lower() != 'y':
            return

    # load netM
    netM = bisenet(PACKAGE_DIR/'net/netM/state_dicts/mosaic_position.pth')

    # load netG
    netG = video(PACKAGE_DIR/'net/netG/state_dicts/clean_youknow_video.pth')

    # output filename
    if time_tag:
        output_file = output_file.with_stem(
            f'{output_file.stem}--'
            f'{start_time.time_tag if start_time else ""}-'
            f'{end_time.time_tag if end_time else ""}')

    # run
    cleaner.run(
        input_file=input_file,
        start_time=start_time,
        end_time=end_time,
        output_file=output_file,
        netM=netM,
        netG=netG,
    )
