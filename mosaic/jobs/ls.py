import click

from mosaic.jobs.manager import Manager
from mosaic.utils.service import service


@click.command
@click.option('-v', '--verbose', is_flag=True, default=False, help='Enable verbose output')
@service(mkdir=False)
def ls(verbose: bool) -> None:
    # search for jobs
    with Manager() as manager:

        # list all jobs
        manager.list_jobs(manager.jobs, verbose=verbose)
