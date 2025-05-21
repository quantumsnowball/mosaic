from pathlib import Path

import click

from mosaic.utils import VideoPathParamType


@click.command
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.argument('output-file', required=True, type=VideoPathParamType())
def create(
    input_file: Path,
    output_file: Path,
) -> None:
    print(f'mosaic jobs create -i {input_file} {output_file}')
