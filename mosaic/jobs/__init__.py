import click

from mosaic.jobs.create import create
from mosaic.jobs.utils import MOSAIC_TEMP_DIR


@click.group(invoke_without_command=True)
@click.pass_context
def jobs(ctx: click.Context) -> None:
    # jobs can be a standalone command
    if ctx.invoked_subcommand:
        return

    for dirpath in MOSAIC_TEMP_DIR.glob('./*/'):
        dirname = dirpath.name
        print(dirname)


jobs.add_command(create)
