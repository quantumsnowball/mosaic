import typer

from mosaic.utils.service import service

from .manager import Manager

app = typer.Typer()


@app.command(
    help='delete jobs',
)
@service(mkdir=False)
def delete() -> None:
    # search for jobs
    with Manager() as manager:

        # prompt for delete a job
        manager.delete_job()
