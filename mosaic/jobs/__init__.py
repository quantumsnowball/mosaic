import click

from mosaic.jobs.clean import clean
from mosaic.jobs.create import create
from mosaic.jobs.ls import ls
from mosaic.jobs.manager import Manager
from mosaic.utils.service import service


@click.group(invoke_without_command=True)
@click.pass_context
@service()
def jobs(ctx: click.Context) -> None:
    # jobs can be a standalone command
    if ctx.invoked_subcommand:
        return

    # create menu and discover jobs
    manager = Manager()

    # prompt for selecting a job
    manager.run_job()


jobs.add_command(create)
jobs.add_command(clean)
jobs.add_command(ls)
