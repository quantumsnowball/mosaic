import importlib.metadata as meta

import click

from mosaic.free import free
from mosaic.remove import remove

NAME = 'mosaic'


@click.group(invoke_without_command=True)
@click.option('-v', '--version', default=False, is_flag=True, help='enable preview mode')
def mosaic(version: bool) -> None:
    if version:
        print(f'v{meta.version(NAME)}')


mosaic.add_command(remove)
mosaic.add_command(free)
