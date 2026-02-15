import os

import click

from mosaic.jobs.clean import clean
from mosaic.jobs.create import create
from mosaic.jobs.delete import delete
from mosaic.jobs.ls import ls
from mosaic.jobs.run import run
from mosaic.jobs.select import select
from mosaic.jobs.tui import Dashboard
from mosaic.utils.service import service


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Enable Textual developer tools")
@click.pass_context
@service()
def jobs(ctx: click.Context, debug: bool) -> None:
    # jobs can be a standalone command
    if ctx.invoked_subcommand:
        return

    if debug:
        os.environ["TEXTUAL"] = "devtools"

    app = Dashboard()
    app.run()


jobs.add_command(create)
jobs.add_command(select)
jobs.add_command(run)
jobs.add_command(clean)
jobs.add_command(delete)
jobs.add_command(ls)
