from typing import Any

import click
from click import style

from mosaic.jobs.job import Job
from mosaic.jobs.utils import JOBS_DIR


def field(
    key: str,
    val: Any,
    width: int = 16,
    *,
    newline: bool = True,
    fg_key: str = 'cyan',
    fg_val: str = 'green',
    dim: bool = False,
) -> str:
    txt_key = style(f'{key:>{width}s}', fg=fg_key, dim=dim)
    txt_val = style(f'{str(val)}', fg=fg_val, dim=dim)
    txt = f'{txt_key}: {txt_val}'
    if newline:
        txt += '\n'
    return txt


def job_info(i: int, job: Job) -> str:
    dim = job.checklist.is_finished

    def title() -> str:
        return style(f'{i+1}: {job.timestamp_pp} - {job.id}', fg='yellow', dim=dim)

    txt = title()
    for key, val in {
        'progress': f'{job.checklist.count_finished} / {job.checklist.count} completed',
        'command': job.command,
        'segment time': job.segment_time,
        'input file': job.input_file,
        'output file': job.output_file,
    }.items():
        txt += field(key, val, dim=dim)
    return txt


class Menu:
    def __init__(self) -> None:
        # detect all jobs available
        self.jobs = [Job.load(dirpath)
                     for dirpath in sorted(JOBS_DIR.glob('./*/'))]

    def list_jobs(self) -> None:
        for i, job in enumerate(self.jobs):
            click.echo(job_info(i, job))

    def prompt(self) -> None:
        if len(self.jobs) > 0:
            n: int = click.prompt('Please select a job', type=int)
            selected_job = self.jobs[n - 1]
            selected_job.run()
        else:
            print('No jobs available. Please create a job first.')
