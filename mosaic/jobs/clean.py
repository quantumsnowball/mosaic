from typing import Annotated

import typer
from typer import Option

from mosaic.utils.service import service

from .manager import Manager

app = typer.Typer()


@app.command(
    help='clean up storage space',
)
@service(mkdir=False)
def clean(
    clear_all_jobs: Annotated[bool, Option('--clear-all-jobs', help='clear all jobs')] = False,
) -> None:
    # search for jobs
    with Manager() as manager:

        # prompt for delete the whole root dir
        if clear_all_jobs:
            manager.clear_all_jobs()
            return

        # default only prompt to clean finished jobs
        manager.clear_finished()
