from pathlib import Path

import click

from mosaic.free.cleaner import cleanmosaic_video_fusion
from mosaic.free.net.netG import video
from mosaic.free.net.netM import bisenet
from mosaic.free.net.util.util import clean_tempfiles
from mosaic.utils import HMS, HMSParamType, VideoPathParamType

TEMP_DIRNAME = '.mosaic'


@click.command()
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.option('-ss', '--start-time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end-time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.argument('output-file', required=True, type=VideoPathParamType())
def free(input_file: Path,
         start_time: HMS | None,
         end_time: HMS | None,
         output_file: Path,
         ) -> None:
    # paths
    this_dir = Path(__file__).parent
    output_dir = output_file.parent

    # verify inputs
    assert input_file.exists(), f'{input_file} does not exists'
    if start_time and end_time:
        if not end_time > start_time:
            raise ValueError('Invalid start time or end time')

    # load netM
    netM = bisenet(this_dir/'net/netM/state_dicts/mosaic_position.pth')

    # load netG
    netG = video(this_dir/'net/netG/state_dicts/clean_youknow_video.pth')

    # run
    cleanmosaic_video_fusion(
        media_path=input_file,
        temp_dir=output_dir/TEMP_DIRNAME,
        result_dir=output_dir,
        start_time=start_time,
        end_time=end_time,
        output_file=output_file,
        netG=netG,
        netM=netM
    )
    click.echo('Finished!')
