import click


@click.group()
def mosaic() -> None:
    pass


@mosaic.command()
def remove() -> None:
    print('mosaic remove')
