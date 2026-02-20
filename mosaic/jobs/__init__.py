import os
from typing import Annotated

import typer

from mosaic.jobs.clean import clean
from mosaic.jobs.create import create
from mosaic.jobs.delete import delete
from mosaic.jobs.ls import ls
from mosaic.jobs.run import app as run
from mosaic.jobs.select import app as select
from mosaic.jobs.tui import Main
from mosaic.utils.service import service

app = typer.Typer()


@app.callback(invoke_without_command=True)
@service()
def jobs(
    ctx: typer.Context,
    debug: Annotated[bool, typer.Option("--debug", help="Enable Textual developer tools")] = False,
) -> None:
    # jobs can be a standalone command
    if ctx.invoked_subcommand is not None:
        return

    # debug mode, to be used with textual console
    if debug:
        os.environ["TEXTUAL"] = "devtools"

    # textual main app
    app = Main()
    app.run()


# jobs.add_command(create)
app.add_typer(select)
app.add_typer(run)
# jobs.add_command(clean)
# jobs.add_command(delete)
# jobs.add_command(ls)
