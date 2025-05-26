import click

from mosaic.jobs.clean import clean
from mosaic.jobs.create import create
from mosaic.jobs.menu import Menu
from mosaic.utils.service import service


@click.group(invoke_without_command=True)
@click.pass_context
@service()
def jobs(ctx: click.Context) -> None:
    # jobs can be a standalone command
    if ctx.invoked_subcommand:
        return

    # create menu and discover jobs
    menu = Menu()

    # display a job list
    menu.list_jobs()

    # prompt for selecting a job
    menu.prompt()


jobs.add_command(create)
jobs.add_command(clean)
