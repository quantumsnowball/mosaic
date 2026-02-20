import importlib.metadata as meta

import typer

from mosaic.free import app as free
from mosaic.jobs import jobs
from mosaic.lada import lada
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

# mosaic.add_command(lada)
# mosaic.add_command(jobs)
