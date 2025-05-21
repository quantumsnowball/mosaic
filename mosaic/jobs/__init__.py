import json
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import click

from mosaic.jobs.create import create
from mosaic.jobs.job import JobInfo
from mosaic.jobs.utils import MOSAIC_TEMP_DIR


def start_job(job_dirpath: Path) -> None:
    job_infopath = job_dirpath / 'job.json'
    with open(job_infopath, 'r') as f:
        info = SimpleNamespace(json.load(f))
        # TODO: you should write imple how to do the job around here
        print(f'\nStarted job {info.id}')
        print(f'{info.command} -i {info.input_file} {info.output_file}')


@click.group(invoke_without_command=True)
@click.pass_context
def jobs(ctx: click.Context) -> None:
    # jobs can be a standalone command
    if ctx.invoked_subcommand:
        return

    # detect all jobs available
    jobs = tuple(MOSAIC_TEMP_DIR.glob('./*/'))

    # display a job list
    for i, dirpath in enumerate(jobs):
        job_infopath = dirpath / 'job.json'
        info = JobInfo.load(job_infopath)
        print(f'{i+1}: {info.id}')
        print(f'\tcommand: {info.command}')
        print(f'\tinput file: {info.input_file}')
        print(f'\toutput file: {info.output_file}')

    # ask to select a job
    selected_job_num = cast(int, click.prompt('Please select a job', type=int))
    selected_job = jobs[selected_job_num - 1]
    start_job(selected_job)


jobs.add_command(create)
