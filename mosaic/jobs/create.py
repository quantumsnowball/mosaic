from pathlib import Path

import click

from mosaic.jobs.job import Job
from mosaic.utils import VideoPathParamType


@click.group
def create() -> None:
    pass


@create.command
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.argument('output-file', required=True, type=VideoPathParamType())
def free(
    input_file: Path,
    output_file: Path,
) -> None:
    # create a new job
    job = Job.create(
        command='free',
        input_file=input_file,
        output_file=output_file,
    )

    # create the job directory
    job.create_dirs()

    # create the meta data json file
    job.save()
