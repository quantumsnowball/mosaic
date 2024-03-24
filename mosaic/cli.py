import click

from mosaic.remove import remove


@click.group()
def mosaic() -> None:
    pass


mosaic.add_command(remove)
