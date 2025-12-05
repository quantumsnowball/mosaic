import click

from mosaic.utils.service import service


@click.command
@service()
def run() -> None:
    print('should start to run all unfinished jobs')
