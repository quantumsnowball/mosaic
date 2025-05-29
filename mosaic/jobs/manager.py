from pathlib import Path
from shutil import rmtree

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
        index = style(f'{i+1}. ', fg='white', dim=dim)
        command = style(f'{job.command:8s}', fg='red', dim=dim)
        info = style(f'{job.timestamp_pp} - {job.id}', fg='green', dim=dim)
        return index + command + info

    def progress() -> str:
        done = job.checklist.count_finished
        total = job.checklist.count

        name = style(f'{" "*indent + "progress":{width}s}', fg='blue', dim=dim)
        pct = style(f'{done / total:.2%}', fg='red', dim=dim)
        count = style(f'{done} / {total}', fg='yellow', dim=dim)
        segment_time = style(f'{job.segment_time}', fg='yellow', dim=dim)
        return f'{name} {pct}, {count} done, {segment_time} each'

    def video_file_details(file: Path, *, tag: str) -> str:
        txt = style(f'{" "*indent + tag:{width}s} ', fg='blue', dim=dim)
        if not file.exists():
            txt += style(f'{str(file)}, ', fg='white', dim=dim) + style('not exist', fg='yellow', dim=dim)
            return txt

        size_mb = round(file.stat().st_size / 1e6, 2)
        metadata = style(f'{size_mb:,.2f} MB', fg='yellow', dim=dim) if file.exists() else ''
        txt += style(f'{str(file)}, ', fg='white', dim=dim) + metadata
        streams = FFprobe(file)
        for i, stream in enumerate(streams.video):
            txt += (
                '\n' + style(f'{" "*indent*2}v:{i} {stream.hms} ', fg='yellow', dim=dim) +
                style(', ', dim=dim).join([style(f'{s}', fg='cyan', dim=dim) for s in stream.summary])
            )
        for i, stream in enumerate(streams.audio):
            txt += (
                '\n' + style(f'{" "*indent*2}a:{i} {stream.hms} ', fg='magenta', dim=dim) +
                style(', ', dim=dim).join([style(f'{s}', fg='cyan', dim=dim) for s in stream.summary])
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
        '',
    ])


class Manager:
    def __init__(self) -> None:
        # detect all jobs available
        self.jobs = [load_job(dirpath)
                     for dirpath in sorted(JOBS_DIR.glob('./*/'))]
        self.jobs_finished = [job for job in self.jobs if job.is_finished]
        self.jobs_unfinished = [job for job in self.jobs if not job.is_finished]

    def list_jobs(self, jobs) -> None:
        for i, job in enumerate(jobs):
            click.echo(job_info(i, job))

    def run_job(self) -> None:
        self.list_jobs(self.jobs_unfinished)
        if len(self.jobs) > 0:
            n: int = click.prompt('Please select a job to run', type=int)
            selected_job = self.jobs[n - 1]
            selected_job.run()
        else:
            print('No jobs available. Please create a job first.')

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
