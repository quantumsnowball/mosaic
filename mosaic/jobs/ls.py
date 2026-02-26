from typing import Annotated

import typer
from typer import Option

from mosaic.utils.service import service

from .manager import Manager

app = typer.Typer()


@app.command(
    help='list jobs info',
)
@service(mkdir=False)
def ls(
    verbose: Annotated[bool, Option('--verbose', '-v', help='enable verbose output')] = False,
) -> None:
    # search for jobs
    with Manager() as manager:

        # list all jobs
        manager.list_jobs(manager.jobs, verbose=verbose)
