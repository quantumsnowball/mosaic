
import click


@click.command()
def jobs() -> None:
    print('list all jobs found in the cwd')
