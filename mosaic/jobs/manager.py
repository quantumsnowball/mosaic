from shutil import rmtree
from typing import Generator, Iterable, Self

from rich.prompt import Confirm, IntPrompt

from mosaic.jobs.job import Job, load_job
from mosaic.jobs.text import job_info
from mosaic.jobs.utils import JOBS_DIR
from mosaic.utils.console import stderr, stdout


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
            stdout(job_info(job, i, verbose=verbose))

    def run_job(self) -> None:
        while True:
            jobs = list(self.jobs_unfinished)
            if len(jobs) == 0:
                stdout('No jobs available. Please create a job first.')
                return

            self.list_jobs(jobs)
            n: int = IntPrompt.ask('Please select an unfinished job to run')
            if n > len(jobs):
                continue

            selected_job = jobs[n - 1]
            selected_job.run()
            return

    def delete_job(self) -> None:
        while True:
            jobs = list(self.jobs)
            if len(jobs) == 0:
                stdout('Job list is empty.')
                return

            self.list_jobs(jobs)
            n: int = IntPrompt.ask('Please select a job to delete')
            if n > len(jobs):
                continue

            selected_job = jobs[n - 1]
            if Confirm.ask(f'[red]Are you sure to DELETE job {selected_job.id}?[/]', default=False):
                rmtree(selected_job.job_dirpath)
                stdout(f'[yellow]Deleted job: {selected_job.id}[/]')

    def clear_finished(self) -> None:
        jobs = list(self.jobs_finished)
        self.list_jobs(jobs)
        if Confirm.ask('Do you want to DELETE ALL finished jobs?', default=False):
            for job in jobs:
                try:
                    rmtree(job.job_dirpath)
                    stdout(f'[yellow]Deleted job: {job.id}[/]')
                except Exception:
                    stderr(f'[red]Failed to delete job: {job.id}[/]')
        else:
            stdout('Operation cancelled')

    def clear_all_jobs(self) -> None:
        jobs = list(self.jobs)
        self.list_jobs(jobs)
        if Confirm.ask('[red]Do you want to DELETE ALL jobs?[/]', default=False):
            for job in jobs:
                try:
                    rmtree(job.job_dirpath)
                    stdout(f'[yellow]Deleted job: {job.id}[/]')
                except Exception:
                    stderr(f'[red]Failed to delete job: {job.id}[/]')

        else:
            stdout('Operation cancelled')
