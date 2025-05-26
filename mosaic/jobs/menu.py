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
) -> str:
    txt_key = style(f'{key:>{width}s}', fg=fg_key)
    txt_val = style(f'{str(val)}', fg=fg_val)
    txt = f'{txt_key}: {txt_val}'
    if newline:
        txt += '\n'
    return txt


class Menu:
    def __init__(self) -> None:
        # detect all jobs available
        self.jobs = [Job.load(dirpath)
                     for dirpath in sorted(JOBS_DIR.glob('./*/'))]

    def list_jobs(self) -> None:
        for i, job in enumerate(self.jobs):
            click.echo((
                f'{i+1}: {job.timestamp_pp} - {job.id}\n' +
                field('progress', f'{job.checklist.count_finished} / {job.checklist.count} completed') +
                field('command', job.command) +
                field('segment time', job.segment_time) +
                field('input file', job.input_file) +
                field('output file', job.output_file)
            ))

    def prompt(self) -> None:
        if len(self.jobs) > 0:
            n: int = click.prompt('Please select a job', type=int)
            selected_job = self.jobs[n - 1]
            selected_job.run()
        else:
            print('No jobs available. Please create a job first.')
