import click


@click.command()
def upscale() -> None:
    click.echo(('TODO: This should upscale a video based on user settings.\n'
                'Should do all interprocess data exchange using pipes, never cache in the slow storage.'))
