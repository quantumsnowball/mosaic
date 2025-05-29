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

    def title() -> str:
        index = style(f'{i+1}. ', fg='white', dim=dim)
        command = style(f'{job.command:8s}', fg='red', dim=dim)
        info = style(f'{job.timestamp_pp} - {job.id}', fg='green', dim=dim)
        return index + command + info

    def progress() -> str:
        name = style(f'{" "*indent + "progress":{width}s} ', fg='blue', dim=dim)
        count = style(f'{job.checklist.count_finished} / {job.checklist.count} completed, ', fg='white', dim=dim)
        segment_time = style(f'segment time {job.segment_time}', fg='white', dim=dim)
        return name + count + segment_time

    def input_file() -> str:
        file = job.input_file
        txt = style(f'{" "*indent + "input file":{width}s} ', fg='blue', dim=dim)
        if not file.exists():
            txt += style(f'{str(file)} (not exist)', fg='white', dim=dim)
            return txt

        size_mb = round(file.stat().st_size / 1e6, 2)
        metadata = f'{size_mb}MB'
        txt += style(f'{str(file)} ({metadata})', fg='white', dim=dim)
        streams = FFprobe(file)
        for i, stream in enumerate(streams.video):
            txt += (
                '\n' + style(f'{" "*indent*2}v:{i} {stream.hms} ', fg='yellow', dim=dim) +
                style(f'{stream.summary()}', fg='cyan', dim=dim)
            )
        for i, stream in enumerate(streams.audio):
            txt += (
                '\n' + style(f'{" "*indent*2}a:{i} {stream.hms} ', fg='magenta', dim=dim) +
                style(f'{stream.summary()}', fg='cyan', dim=dim)
            )
        return txt

    def output_file() -> str:
        file = job.output_file
        txt = style(f'{" "*indent + "output file":{width}s} ', fg='blue', dim=dim)
        if not file.exists():
            txt += style(f'{str(file)} (not exist)', fg='white', dim=dim)
            return txt

        size_mb = round(file.stat().st_size / 1e6, 2)
        metadata = f'{size_mb}MB' if file.exists() else ''
        txt += style(f'{str(file)} ({metadata})', fg='white', dim=dim)
        streams = FFprobe(file)
        for i, stream in enumerate(streams.video):
            txt += (
                '\n' + style(f'{" "*indent*2}v:{i} {stream.hms} ', fg='yellow', dim=dim) +
                style(f'{stream.summary()}', fg='cyan', dim=dim)
            )
        for i, stream in enumerate(streams.audio):
            txt += (
                '\n' + style(f'{" "*indent*2}a:{i} {stream.hms} ', fg='magenta', dim=dim) +
                style(f'{stream.summary()}', fg='cyan', dim=dim)
            )
        return txt

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
