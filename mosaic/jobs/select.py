import click

from mosaic.jobs.manager import Manager
from mosaic.utils.service import service


@click.command
@service()
def select() -> None:
    # create menu and discover jobs
    with Manager() as manager:
        # prompt for selecting a job
        manager.run_job()
