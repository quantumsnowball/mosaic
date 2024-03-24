import shutil
from pathlib import Path

import click

from mosaic.remove.command import DeepMosaicsCommand
from mosaic.utils import HMS, HMSParamType, VideoPathParamType, clean_up

CACHE_DIRNAME = '.mosaic'


@click.command()
@click.option('-i', '--input', required=True, type=VideoPathParamType(), help='input media path')
@click.option('-ss', '--start_time', default=None, type=HMSParamType(), help='start time in HH:MM:SS')
@click.option('-to', '--end_time', default=None, type=HMSParamType(), help='end time in HH:MM:SS')
@click.option('--model_path', default=None, type=VideoPathParamType(), help='pretrained model path')
@click.option('--preview', default=False, is_flag=True, help='enable preview mode')
@click.option('--dry-run', default=False, is_flag=True, help='only show the command, not actual run')
@click.argument('output', required=True, type=VideoPathParamType())
def remove(input: Path,
           start_time: HMS | None,
           end_time: HMS | None,
           model_path: Path | None,
           preview: bool,
           dry_run: bool,
           output: Path,
           ) -> None:
    # create command for DeepMosaics
    dm = DeepMosaicsCommand(
        root=Path(__file__).parent.parent,
        media_path=input,
        start_time=start_time,
        end_time=end_time,
        preview=preview,
        result_dir=output.parent / CACHE_DIRNAME / output.name,
        model_path=model_path
    )

    # preview command
    if dry_run:
        dm.pprint()
        return

    # run command
    dm.run()

    # move result to target path
    shutil.move(dm.result_file, output)

    # clean
    clean_up(dm.result_dir)
