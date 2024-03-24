import subprocess
from pathlib import Path

import click


@click.group()
def mosaic() -> None:
    pass


@mosaic.command()
def remove() -> None:
    cwd = Path(__file__).parent
    deepmosaic_path = cwd / 'DeepMosaics' / 'deepmosaic.py'
    subprocess.run(['python', deepmosaic_path])
