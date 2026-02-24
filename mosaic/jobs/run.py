import rich
import typer

from mosaic.utils.logging import log
from mosaic.utils.service import service

from .manager import Manager
from .text import job_info

app = typer.Typer()


@app.command()
@service()
def run() -> None:
    # create menu and discover jobs
    with Manager() as manager:
        while (job := next(manager.jobs_unfinished, None)):
            # get the next unfinished job to run
            rich.print(job_info(job))
            try:
                job.run(force_overwrite=True)
            except KeyboardInterrupt as e:
                log.info(e.__class__)
                break
