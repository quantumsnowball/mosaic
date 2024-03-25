from pathlib import Path

import click

from mosaic.free.net.clean import cleanmosaic_video_fusion
from mosaic.free.net.netG import video
from mosaic.free.net.netM import bisenet
from mosaic.free.net.util.util import clean_tempfiles
from mosaic.utils import HMS, HMSParamType, VideoPathParamType

TEMP_DIRNAME = '.mosaic'


@click.command()
@click.option('-i', '--input', required=True, type=VideoPathParamType(), help='input media path')
@click.option('-ss', '--start-time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end-time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.option('--model-file', default=None, type=VideoPathParamType(), help='pretrained model path')
@click.argument('output-file', required=True, type=VideoPathParamType())
def free(input: Path,
         start_time: HMS | None,
         end_time: HMS | None,
         model_file: Path | None,
         output_file: Path,
         ) -> None:

    this_dir = Path(__file__).parent
    output_dir = output_file.parent

    # load netM
    netM_state = this_dir / 'net/netM/state_dicts/mosaic_position.pth'
    netM = bisenet(netM_state)
    # print(netM)
    netG_state = this_dir / 'net/netG/state_dicts/clean_youknow_video.pth'
    netG = video(netG_state)
    # print(netG)
    cleanmosaic_video_fusion(media_path=input,
                             temp_dir=output_dir/TEMP_DIRNAME,
                             result_dir=output_dir,
                             start_time=start_time,
                             end_time=end_time,
                             output_file=output_file,
                             netG=netG,
                             netM=netM)
    print('Finished!')
