import click

from mosaic.jobs.clean import clean
from mosaic.jobs.create import create
from mosaic.jobs.job import Job
from mosaic.jobs.utils import JOBS_DIR
from mosaic.utils.service import service


@click.group(invoke_without_command=True)
@click.pass_context
@service(mkdir=False)
def jobs(ctx: click.Context) -> None:
    # jobs can be a standalone command
    if ctx.invoked_subcommand:
        return

    # detect all jobs available
    jobs = [Job.load(dirpath)
            for dirpath in tuple(JOBS_DIR.glob('./*/'))]

    # display a job list
    for i, job in enumerate(jobs):
        print(f'{i+1}: {job.id}')
        print(f'\tcommand: {job.command}')
        print(f'\tinput file: {job.input_file}')
        print(f'\toutput file: {job.output_file}')

    # ask to select a job
    if len(jobs) > 0:
        n: int = click.prompt('Please select a job', type=int)
        selected_job = jobs[n - 1]
        selected_job.run()
    else:
        print('No jobs available. Please create a job first.')


jobs.add_command(create)
jobs.add_command(clean)
