import importlib.metadata as meta

import click

from mosaic.free import free
from mosaic.remove import remove

NAME = 'mosaic'


@click.group()
def mosaic() -> None:
    pass


@mosaic.command
def version() -> None:
    print(f'v{meta.version(NAME)}')


mosaic.add_command(remove)
mosaic.add_command(free)
