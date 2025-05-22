from shutil import rmtree

import click

from mosaic.jobs.utils import JOBS_DIR


@click.command
@click.option('--clear-all-jobs', is_flag=True, default=False, help='clear all jobs')
def clean(clear_all_jobs: bool) -> None:
    # prompt for delete the whole mosaic temp dir
    if clear_all_jobs:
        if click.prompt(
            'Do you want to DELETE ALL unfinished jobs (y/N)?',
            type=str,
            default='n',
            show_default=False,
        ).lower() == 'y':
            rmtree(JOBS_DIR, ignore_errors=True)
            if not JOBS_DIR.exists():
                click.echo('All jobs has been cleared')
        else:
            click.echo('Operation cancelled')
        return
