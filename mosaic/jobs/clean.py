from shutil import rmtree

import click

from mosaic.jobs.manager import Manager
from mosaic.jobs.utils import JOBS_DIR
from mosaic.utils.service import service


@click.command
@click.option('--clear-all-jobs', is_flag=True, default=False, help='clear all jobs')
@service(mkdir=False)
def clean(clear_all_jobs: bool) -> None:
    # search for jobs
    manager = Manager()

    # prompt for delete the whole root dir
    if clear_all_jobs:
        manager.clear_all_jobs()
        return

    # default only prompt to clean finished jobs
    manager.clear_finished()
