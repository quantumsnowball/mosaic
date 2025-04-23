from pathlib import Path

import click

from mosaic.upscale import upscaler
from mosaic.upscale.net.real_esrgan import RealESRGANer
from mosaic.utils import HMS, HMSParamType, VideoPathParamType

PACKAGE_DIR = Path(__file__).parent


@click.command()
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.option('-ss', '--start-time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end-time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.option('-x', '--scale', default='2', type=click.Choice(('2', '4')), help='up sampling scaling, can be 2x or 4x')
@click.option('-y', '--force', is_flag=True, default=False, help='overwrite output file without asking')
@click.argument('output-file', required=True, type=VideoPathParamType())
def upscale(input_file: Path,
            start_time: HMS | None,
            end_time: HMS | None,
            scale: str,
            force: bool,
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

    # load upsampler
    upsampler = RealESRGANer(
        scale=int(scale),
        model_path=PACKAGE_DIR/f'net/state_dicts/RealESRGAN_x{scale}plus.pth',
        gpu_id=0,
    )

    upscaler.run(
        input_file=input_file,
        start_time=start_time,
        end_time=end_time,
        output_file=output_file,
        upsampler=upsampler,
    )
