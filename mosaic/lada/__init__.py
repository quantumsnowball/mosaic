import click

from mosaic.utils.service import service


@click.command()
@service()
def lada() -> None:
    # run
    print('lada sub-command')
