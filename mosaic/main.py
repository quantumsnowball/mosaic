import importlib.metadata as meta

import typer

from .free import app as free
from .jobs import app as jobs
from .lada import app as lada
from .upscale import app as upscale
from .utils.logging import setup_logger

setup_logger()

NAME = 'mosaic'


app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    '''
    mosaic: a multi-feature video restoration tool
    '''
    pass


@app.command()
def version() -> None:
    print(f'v{meta.version(NAME)}')


app.add_typer(free)
app.add_typer(upscale)
app.add_typer(lada)
app.add_typer(jobs, name='jobs')
