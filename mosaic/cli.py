import os
import signal
import subprocess
from pathlib import Path

import click

from mosaic.utils import HMS, HMSParamType


@click.group()
def mosaic() -> None:
    pass


@mosaic.command()
@click.option('-i', '--input', required=True, type=str, help='input media path')
@click.option('-ss', '--start_time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-t', '--last_time', default=None, type=HMSParamType(), help='last time in HH:MM:SS')
@click.option('--model_path', default=None, type=str, help='pretrained model path')
@click.argument('output', required=True, type=str)
def remove(input: str,
           output: str,
           start_time: HMS | None,
           last_time: HMS | None,
           model_path: str | None) -> None:
    #
    # path
    #
    working_dir = Path(__file__).parent
    deepmosaic_path = str(working_dir / 'DeepMosaics' / 'deepmosaic.py')
    media_path = input
    result_dir = str(Path(output).parent)
    default_model_path = str(working_dir/'DeepMosaics'/'pretrained_models'/'clean_youknow_video.pth')
    model_path = model_path if model_path is not None else default_model_path

    #
    # args
    #
    args = []
    args += ['--mode', 'clean']
    args += ['--no_preview']
    args += ['--media_path', media_path]
    if start_time and last_time:
        if not last_time > start_time:
            click.echo('Invalid time')
        args += ['--start_time', str(start_time)]
        args += ['--last_time', str(last_time)]
    args += ['--result_dir', result_dir]
    args += ['--model_path', model_path]

    #
    # run
    #
    command = ['python', deepmosaic_path] + args
    click.echo(' '.join(command))
    breakpoint()
    # run in process group
    proc = subprocess.Popen(command, preexec_fn=os.setsid)
    try:
        proc.wait()
    except KeyboardInterrupt:
        os.killpg(proc.pid, signal.SIGTERM)
