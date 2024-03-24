import os
import signal
import subprocess
from pathlib import Path

import click

from mosaic.utils import HMS, HMSParamType


@click.command()
@click.option('-i', '--input', required=True, type=str, help='input media path')
@click.option('-ss', '--start_time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end_time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.option('--model_path', default=None, type=str, help='pretrained model path')
@click.option('--preview', default=False, is_flag=True, help='enable preview mode')
@click.option('--dry-run', default=False, is_flag=True, help='only show the command, not actual run')
@click.argument('output', required=True, type=str)
def remove(input: str,
           start_time: HMS | None,
           end_time: HMS | None,
           model_path: str | None,
           preview: bool,
           dry_run: bool,
           output: str,
           ) -> None:
    #
    # path
    #
    root_package_dir = Path(__file__).parent.parent
    deepmosaic_path = str(root_package_dir / 'DeepMosaics' / 'deepmosaic.py')
    media_path = input
    result_dir = str(Path(output).parent)
    default_model_path = str(root_package_dir/'DeepMosaics'/'pretrained_models'/'clean_youknow_video.pth')
    model_path = model_path if model_path is not None else default_model_path

    #
    # args
    #
    args = []
    args += ['--mode', 'clean']
    if not preview:
        args += ['--no_preview']
    args += ['--media_path', media_path]
    if start_time and end_time:
        if not end_time > start_time:
            click.echo('Invalid start time or end time')
        last_time = str(end_time - start_time)
        args += ['--start_time', str(start_time)]
        args += ['--last_time', str(last_time)]
    args += ['--result_dir', result_dir]
    args += ['--model_path', model_path]

    #
    # run
    #
    command = ['python', deepmosaic_path] + args
    click.echo(' '.join(command))
    if dry_run:
        return
    # run in process group
    proc = subprocess.Popen(command, preexec_fn=os.setsid)
    try:
        proc.wait()
    except KeyboardInterrupt:
        os.killpg(proc.pid, signal.SIGTERM)
