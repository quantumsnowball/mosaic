from pathlib import Path

import click

from mosaic.upscale.net import PRESETS, presets
from mosaic.upscale.net.real_esrgan import RealESRGANer
from mosaic.upscale.upscaler import Upscaler
from mosaic.utils import VideoPathParamType
from mosaic.utils.logging import log
from mosaic.utils.service import service
from mosaic.utils.time import HMS, HMSParamType

PACKAGE_DIR = Path(__file__).parent


@click.command()
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.option('-ss', '--start-time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end-time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.option('-m', '--model', default='realesr_animevideov3', type=click.Choice(PRESETS), help='Real-ESRGAN model choices')
@click.option('-s', '--scale', default='1080p', type=click.Choice(('720p', '1080p', '1440p', '2160p')), help='output scale')
@click.option('-y', '--force', is_flag=True, default=False, help='overwrite output file without asking')
@click.option('--raw-info', is_flag=True, default=False, help='display raw ffmpeg info')
@click.argument('output-file', required=True, type=VideoPathParamType())
@service()
def upscale(
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    model: str,
    scale: str,
    force: bool,
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

    # load upsampler
    net = presets[model]
    upsampler = RealESRGANer(
        scale=net.scale,
        model_path=net.model_path,
        model=net.model,
        gpu_id=0,
    )

    with Upscaler(
        input_file=input_file,
        start_time=start_time,
        end_time=end_time,
        output_file=output_file,
        scale=scale,
        raw_info=raw_info,
        upsampler=upsampler,
    ) as upscaler:
        try:
            upscaler.run()
        except KeyboardInterrupt as e:
            log.info(e.__class__)
            upscaler.stop()
