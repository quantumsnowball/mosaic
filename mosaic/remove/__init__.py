import os
import signal
import subprocess
from pathlib import Path

import click

from mosaic.remove.command import DeepMosaicsCommand
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
    command = DeepMosaicsCommand(
        root=Path(__file__).parent.parent,
        media_path=input,
        start_time=start_time,
        end_time=end_time,
        preview=preview,
        result_dir=str(Path(output).parent),
        model_path=model_path
    )

    click.echo(str(command))
    if dry_run:
        return
    # run in process group
    proc = subprocess.Popen(command.tokens, preexec_fn=os.setsid)
    try:
        proc.wait()
    except KeyboardInterrupt:
        os.killpg(proc.pid, signal.SIGTERM)
