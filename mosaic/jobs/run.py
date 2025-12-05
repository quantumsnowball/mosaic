import click

from mosaic.jobs.manager import Manager
from mosaic.utils.service import service


@click.command
@service()
def run() -> None:
    # create menu and discover jobs
    with Manager() as manager:
        while (job := next(manager.jobs_unfinished, None)):
            # get the next unfinished job to run
            job.run(force_overwrite=True)
