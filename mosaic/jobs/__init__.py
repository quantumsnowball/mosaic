import click

from mosaic.jobs.create import create


@click.group(invoke_without_command=True)
@click.pass_context
def jobs(ctx: click.Context) -> None:
    if ctx.invoked_subcommand:
        return

    print('list all jobs found in the cwd')


jobs.add_command(create)
