import importlib.metadata as meta

import click

from mosaic.free_old import free
from mosaic.remove import remove
from mosaic.upscale import upscale

NAME = 'mosaic'


@click.group()
@click.option('-d', '--debug', is_flag=True, help='Enable debugging with PuDB')
def mosaic(debug: bool) -> None:
    if debug:
        import pudb
        pudb.set_trace()
    pass


@mosaic.command
def version() -> None:
    print(f'v{meta.version(NAME)}')


mosaic.add_command(remove)
mosaic.add_command(free)
mosaic.add_command(upscale)
