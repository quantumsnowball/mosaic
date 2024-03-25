from pathlib import Path

import click

from mosaic.free.net.netM import bisenet
from mosaic.utils import HMS, HMSParamType, VideoPathParamType


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
    click.echo('mosaic free')
    print(input)
    print(start_time)
    print(end_time)
    print(model_file)
    print(output_file)

    # load netM
    cwd = Path(__file__).parent
    netM_state = cwd / 'net/netM/state_dicts/mosaic_position.pth'
    netM = bisenet(netM_state)
