from typing import Any

import click
from click import style

from mosaic.jobs.job import Job
from mosaic.jobs.utils import JOBS_DIR


def job_info(i: int, job: Job) -> str:
    dim = job.is_finished
    width = 16

    def title() -> str:
        return style(f'{i+1}: {job.timestamp_pp} - {job.id}', fg='yellow', dim=dim)

    def progress() -> str:
        return (
            style(f'{"progress":>{width}s}: ', fg='cyan', dim=dim) +
            style(f'{job.checklist.count_finished} / {job.checklist.count} completed', fg='green', dim=dim)
        )

    def segment_time() -> str:
        return (
            style(f'{"segment time":>{width}s}: ', fg='cyan', dim=dim) +
            style(f'{job.segment_time}', fg='green', dim=dim)
        )

    def input_file() -> str:
        file = job.input_file
        try:
            size_mb = round(file.stat().st_size / 1e6, 2)
            metadata = f'({size_mb}MB)' if file.exists() else ''
        except FileNotFoundError:
            metadata = '(not exist)'
        return (
            style(f'{"input file":>{width}s}: ', fg='cyan', dim=dim) +
            style(' '.join((str(file), metadata)), fg='green', dim=dim)
        )

    def output_file() -> str:
        file = job.output_file
        try:
            size_mb = round(file.stat().st_size / 1e6, 2)
            metadata = f'({size_mb}MB)' if file.exists() else ''
        except FileNotFoundError:
            metadata = '(not exist)'
        return (
            style(f'{"output file":>{width}s}: ', fg='cyan', dim=dim) +
            style(' '.join((str(file), metadata)), fg='green', dim=dim)
        )

    return '\n'.join([
        title(),
        progress(),
        segment_time(),
        input_file(),
        output_file(),
    ])


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
