import importlib.metadata as meta

import typer

from mosaic.free import app as free
from mosaic.jobs import app as jobs
from mosaic.lada import app as lada
from mosaic.upscale import app as upscale
from mosaic.utils.logging import setup_logger

setup_logger()

NAME = 'mosaic'


app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """
    mosaic: a multi-feature video restoration tool
    """
    pass


@app.command()
def version() -> None:
    print(f'v{meta.version(NAME)}')


app.add_typer(free)
app.add_typer(upscale)
app.add_typer(lada)
app.add_typer(jobs, name='jobs')
