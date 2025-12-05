import click

from mosaic.jobs.manager import Manager, job_info
from mosaic.utils.logging import log
from mosaic.utils.service import service


@click.command
@service()
def run() -> None:
    # create menu and discover jobs
    with Manager() as manager:
        while (job := next(manager.jobs_unfinished, None)):
            # get the next unfinished job to run
            click.echo(job_info(job))
            try:
                job.run(force_overwrite=True)
            except KeyboardInterrupt as e:
                log.info(e.__class__)
                break
