import os
from typing import Annotated

import typer

from mosaic.utils.service import service

from .clean import app as clean
from .create import app as create
from .delete import app as delete
from .ls import app as ls
from .run import app as run
from .select import app as select
from .tui import Main

app = typer.Typer(
    name='jobs',
    help='manage jobs',
)


@app.callback(invoke_without_command=True)
@service()
def jobs(
    ctx: typer.Context,
    debug: Annotated[bool, typer.Option('--debug', help='Enable Textual developer tools')] = False,
) -> None:
    # jobs can be a standalone command
    if ctx.invoked_subcommand is not None:
        return

    # debug mode, to be used with textual console
    if debug:
        os.environ['TEXTUAL'] = 'devtools'

    # textual main app
    app = Main()
    app.run()


app.add_typer(create, name='create')
app.add_typer(select)
app.add_typer(run)
app.add_typer(clean)
app.add_typer(delete)
app.add_typer(ls)
