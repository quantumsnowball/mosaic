import typer

from mosaic.utils.service import service

from .manager import Manager

app = typer.Typer()


@app.command()
@service()
def select() -> None:
    # create menu and discover jobs
    with Manager() as manager:
        # prompt for selecting a job
        manager.run_job()
