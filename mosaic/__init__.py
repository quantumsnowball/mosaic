import importlib.metadata as meta

import click

from mosaic.free import free
from mosaic.jobs import jobs
from mosaic.upscale import upscale
from mosaic.utils.logging import setup_logger

setup_logger()

NAME = 'mosaic'


@click.group()
def mosaic() -> None:
    pass


@mosaic.command
def version() -> None:
    print(f'v{meta.version(NAME)}')


mosaic.add_command(free)
mosaic.add_command(upscale)
mosaic.add_command(jobs)
