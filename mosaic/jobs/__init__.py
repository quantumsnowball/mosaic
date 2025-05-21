import json
from types import SimpleNamespace

import click

from mosaic.jobs.create import create
from mosaic.jobs.utils import MOSAIC_TEMP_DIR


@click.group(invoke_without_command=True)
@click.pass_context
def jobs(ctx: click.Context) -> None:
    # jobs can be a standalone command
    if ctx.invoked_subcommand:
        return

    for i, dirpath in enumerate(MOSAIC_TEMP_DIR.glob('./*/')):
        dirname = dirpath.name
        print(f'{i+1}: {dirname}')
        job_infopath = dirpath / 'job.json'
        with open(job_infopath, 'r') as f:
            info = SimpleNamespace(json.load(f))
            print(f'\tcommand: {info.command}')
            print(f'\tinput file: {info.input_file}')
            print(f'\toutput file: {info.output_file}')


jobs.add_command(create)
