from shutil import rmtree

import click

from mosaic.jobs.manager import Manager
from mosaic.jobs.utils import JOBS_DIR
from mosaic.utils.service import service


@click.command
@click.option('--clear-all-jobs', is_flag=True, default=False, help='clear all jobs')
@service(mkdir=False)
def clean(clear_all_jobs: bool) -> None:
    # prompt for delete the whole root dir
    if clear_all_jobs:
        if click.prompt(
            'Do you want to DELETE ALL unfinished jobs (y/N)?',
            type=str,
            default='n',
            show_default=False,
        ).lower() == 'y':
            rmtree(JOBS_DIR, ignore_errors=True)
            if not JOBS_DIR.exists():
                click.echo('All jobs and temp files have been cleared')
        else:
            click.echo('Operation cancelled')
        return

    # default only prompt to clean finished jobs
    manager = Manager()
    manager.list_jobs()
    manager.clear_finished()
