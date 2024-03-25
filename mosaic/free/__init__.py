import click


@click.command()
def free() -> None:
    click.echo('mosaic free')
