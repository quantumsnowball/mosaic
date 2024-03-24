import shutil
from pathlib import Path

import click

from mosaic.remove.command import DeepMosaicsCommand
from mosaic.utils import HMS, HMSParamType, clean_up_cache


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
    output_dir = Path(output).parent
    output_fname = Path(output).name
    result_dir = str(output_dir / '.mosaic' / output_fname) + '/'

    # create command for DeepMosaics
    dm = DeepMosaicsCommand(
        root=Path(__file__).parent.parent,
        media_path=input,
        start_time=start_time,
        end_time=end_time,
        preview=preview,
        result_dir=result_dir,
        model_path=model_path
    )

    # preview command
    if dry_run:
        dm.pprint()
        return

    # run command
    dm.run()

    # move result to target path
    result = Path(result_dir) / f'{str(Path(input).stem)}_clean.mp4'
    shutil.move(result, Path(output))

    # clean
    clean_up_cache(Path(result_dir))
