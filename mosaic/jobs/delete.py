import typer

from mosaic.jobs.manager import Manager
from mosaic.utils.service import service

app = typer.Typer()


@app.command()
@service(mkdir=False)
def delete() -> None:
    # search for jobs
    with Manager() as manager:

        # prompt for delete a job
        manager.delete_job()
