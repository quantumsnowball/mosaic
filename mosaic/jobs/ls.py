import click

from mosaic.jobs.manager import Manager
from mosaic.utils.service import service


@click.command
@service(mkdir=False)
def ls() -> None:
    # search for jobs
    with Manager() as manager:

        # list all jobs
        manager.list_jobs(manager.jobs)
