from pathlib import Path

import click

from mosaic.jobs.utils import MOSAIC_TEMP_DIR
from mosaic.utils import VideoPathParamType


@click.group
def create() -> None:
    pass


@create.command
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.argument('output-file', required=True, type=VideoPathParamType())
def free(
    input_file: Path,
    output_file: Path,
) -> None:
    # create the mosaic temp dir if not exists
    Path.mkdir(MOSAIC_TEMP_DIR, exist_ok=True)
