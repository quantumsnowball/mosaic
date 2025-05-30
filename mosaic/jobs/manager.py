from pathlib import Path
from shutil import rmtree
from typing import Self

import click
from click import style

from mosaic.jobs.job import load_job
from mosaic.jobs.job.base import Job
from mosaic.jobs.utils import JOBS_DIR
from mosaic.utils.ffprobe import FFprobe


def job_info(i: int, job: Job) -> str:
    dim = job.is_finished
    width = 16
    indent = 2

    def r(txt: str) -> str:
        return style(txt, fg='red', dim=dim)

    def g(txt: str) -> str:
        return style(txt, fg='green', dim=dim)

    def y(txt: str) -> str:
        return style(txt, fg='yellow', dim=dim)

    def b(txt: str) -> str:
        return style(txt, fg='blue', dim=dim)

    def m(txt: str) -> str:
        return style(txt, fg='magenta', dim=dim)

    def c(txt: str) -> str:
        return style(txt, fg='cyan', dim=dim)

    def w(txt: str) -> str:
        return style(txt, fg='white', dim=dim)

    def title() -> str:
        index = f'{i+1}. '
        command = f'{job.command:8s}'
        info = f'{job.timestamp_pp} - {job.id}'
        return (
            w(index) + r(command) + g(info)
        )

    def progress() -> str:
        done = job.checklist.count_finished
        total = job.checklist.count

        name = f'{" "*indent + "progress":{width}s} '
        pct = f'{done / total:.2%}'
        count = f'{done} / {total}'
        segment_time = f'{job.segment_time}'
        return (
            b(name) +
            r(pct) + w(', ') +
            y(count) + w(' done, ') +
            y(segment_time) + w(' each')
        )

    def video_file_details(file: Path, *, tag: str) -> str:
        txt = b(f'{" "*indent + tag:{width}s} ')
        if not file.exists():
            txt += w(f'{str(file)}, ') + y('not exist')
            return txt

        size_mb = round(file.stat().st_size / 1e6, 2)
        txt += w(f'{str(file)} ') + y(f'{size_mb:,.2f} MB')
        details = FFprobe(file)
        for i, stream in enumerate(details.video):
            txt += (
                y(f'\n{" "*indent*2}v:{i} {stream.hms} ') +
                w(', ').join([c(f'{s}') for s in stream.summary])
            )
        for i, stream in enumerate(details.audio):
            txt += (
                m(f'\n{" "*indent*2}a:{i} {stream.hms} ') +
                w(', ').join([c(f'{s}') for s in stream.summary])
            )
        return txt

    def input_file() -> str:
        file = job.input_file
        return video_file_details(file, tag='input file')

    def output_file() -> str:
        file = job.output_file
        return video_file_details(file, tag='output file')

    return '\n'.join([
        title(),
        progress(),
        input_file(),
        output_file(),
    ]) + '\n'


class Manager:
    def __init__(self) -> None:
        # detect all jobs available
        self.jobs = [load_job(dirpath)
                     for dirpath in sorted(JOBS_DIR.glob('./*/'))]
        self.jobs_finished = [job for job in self.jobs if job.is_finished]
        self.jobs_unfinished = [job for job in self.jobs if not job.is_finished]

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        try:
            JOBS_DIR.rmdir()
        except OSError:
            pass

    def list_jobs(self, jobs) -> None:
        for i, job in enumerate(jobs):
            click.echo(job_info(i, job))

    def run_job(self) -> None:
        if len(self.jobs_unfinished) == 0:
            click.echo('No jobs available. Please create a job first.')
            return

        self.list_jobs(self.jobs_unfinished)
        n: int = click.prompt('Please select an unfinished job to run', type=int)
        selected_job = self.jobs[n - 1]
        selected_job.run()

    def clear_finished(self) -> None:
        self.list_jobs(self.jobs_finished)
        if click.prompt('Do you want to DELETE ALL finished jobs (y/N)?', type=str).lower() == 'y':
            for job in self.jobs_finished:
                try:
                    rmtree(job.job_dirpath)
                    click.secho(f'Deleted job: {job.id}', fg='yellow')
                except Exception:
                    click.secho(f'Failed to delete job: {job.id}', fg='red')
        else:
            click.echo('Operation cancelled')

    def clear_all_jobs(self) -> None:
        self.list_jobs(self.jobs)
        if click.prompt(style('Do you want to DELETE ALL jobs (y/N)?', fg='red'), type=str).lower() == 'y':
            for job in self.jobs:
                try:
                    rmtree(job.job_dirpath)
                    click.secho(f'Deleted job: {job.id}', fg='yellow')
                except Exception:
                    click.secho(f'Failed to delete job: {job.id}', fg='red')

        else:
            click.echo('Operation cancelled')
