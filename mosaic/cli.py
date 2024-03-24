import subprocess
from pathlib import Path

import click


@click.group()
def mosaic() -> None:
    pass


@mosaic.command()
@click.option('-i', '--input', required=True, type=str, help='input media path')
@click.option('--model_path', default=None, type=str, help='pretrained model path')
@click.argument('output', required=True, type=str)
def remove(input: str,
           output: str,
           model_path: str | None) -> None:
    # path
    working_dir = Path(__file__).parent
    deepmosaic_path = str(working_dir / 'DeepMosaics' / 'deepmosaic.py')
    media_path = input
    result_dir = str(Path(output).parent)
    default_model_path = str(working_dir/'DeepMosaics'/'pretrained_models'/'clean_youknow_video.pth')
    model_path = model_path if model_path is not None else default_model_path

    # args
    args = []
    args += ['--mode', 'clean']
    args += ['--no_preview']
    args += ['--media_path', media_path]
    args += ['--result_dir', result_dir]
    args += ['--model_path', model_path]

    # run
    command = ['python', deepmosaic_path] + args
    print(' '.join(command))
    # subprocess.run(command)
