import click

from mosaic.jobs.job import Job
from mosaic.jobs.utils import JOBS_DIR


class Menu:
    def __init__(self) -> None:
        # detect all jobs available
        self.jobs = [Job.load(dirpath)
                     for dirpath in sorted(JOBS_DIR.glob('./*/'))]

    def list_jobs(self) -> None:

        for i, job in enumerate(self.jobs):
            print(f'{i+1}: {job.timestamp_pp} - {job.id}')
            print(f'\tprogress: {job.checklist.count_finished} / {job.checklist.count} completed')
            print(f'\tcommand: {job.command}')
            print(f'\tsegment time: {job.segment_time}')
            print(f'\tinput file: {job.input_file}')
            print(f'\toutput file: {job.output_file}')
            print('')

    def prompt(self) -> None:
        if len(self.jobs) > 0:
            n: int = click.prompt('Please select a job', type=int)
            selected_job = self.jobs[n - 1]
            selected_job.run()
        else:
            print('No jobs available. Please create a job first.')
