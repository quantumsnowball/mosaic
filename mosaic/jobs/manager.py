from shutil import rmtree
from typing import Generator, Iterable, Self

import click
import rich
from click import style

from mosaic.jobs.job import load_job
from mosaic.jobs.job.base import Job
from mosaic.jobs.text import job_info
from mosaic.jobs.utils import JOBS_DIR


class Manager:
    @property
    def jobs(self) -> Generator[Job]:
        # detect all jobs available
        return (load_job(dirpath) for dirpath in sorted(JOBS_DIR.glob('./*/')))

    @property
    def jobs_finished(self) -> Generator[Job]:
        return (job for job in self.jobs if job.is_finished)

    @property
    def jobs_unfinished(self) -> Generator[Job]:
        return (job for job in self.jobs if not job.is_finished)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        try:
            JOBS_DIR.rmdir()
        except OSError:
            pass

    def list_jobs(self, jobs: Iterable[Job], *, verbose: bool = False) -> None:
        for i, job in enumerate(jobs):
            rich.print(job_info(job, i, verbose=verbose))

    def run_job(self) -> None:
        while True:
            jobs = list(self.jobs_unfinished)
            if len(jobs) == 0:
                click.echo('No jobs available. Please create a job first.')
                return

            self.list_jobs(jobs)
            n: int = click.prompt('Please select an unfinished job to run', type=int)
            if n > len(jobs):
                continue

            selected_job = jobs[n - 1]
            selected_job.run()
            return

    def delete_job(self) -> None:
        while True:
            jobs = list(self.jobs)
            if len(jobs) == 0:
                click.echo('Job list is empty.')
                return

            self.list_jobs(jobs)
            n: int = click.prompt('Please select a job to delete', type=int)
            if n > len(jobs):
                continue

            selected_job = jobs[n - 1]
            if click.prompt(style(f'Are you sure to DELETE job {selected_job.id} (y/N)?', fg='red'), type=str).lower() == 'y':
                rmtree(selected_job.job_dirpath)
                click.secho(f'Deleted job: {selected_job.id}', fg='yellow')

    def clear_finished(self) -> None:
        jobs = list(self.jobs_finished)
        self.list_jobs(jobs)
        if click.prompt('Do you want to DELETE ALL finished jobs (y/N)?', type=str).lower() == 'y':
            for job in jobs:
                try:
                    rmtree(job.job_dirpath)
                    click.secho(f'Deleted job: {job.id}', fg='yellow')
                except Exception:
                    click.secho(f'Failed to delete job: {job.id}', fg='red')
        else:
            click.echo('Operation cancelled')

    def clear_all_jobs(self) -> None:
        jobs = list(self.jobs)
        self.list_jobs(jobs)
        if click.prompt(style('Do you want to DELETE ALL jobs (y/N)?', fg='red'), type=str).lower() == 'y':
            for job in jobs:
                try:
                    rmtree(job.job_dirpath)
                    click.secho(f'Deleted job: {job.id}', fg='yellow')
                except Exception:
                    click.secho(f'Failed to delete job: {job.id}', fg='red')

        else:
            click.echo('Operation cancelled')
