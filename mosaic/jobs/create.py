from pathlib import Path

import click

from mosaic.jobs.job import Job
from mosaic.utils import VideoPathParamType
from mosaic.utils.service import service


@click.group
def create() -> None:
    pass


@create.command
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.argument('output-file', required=True, type=VideoPathParamType())
@service()
def free(
    input_file: Path,
    output_file: Path,
) -> None:
    # create a new job
    with Job.create(
        command='free',
        input_file=input_file,
        output_file=output_file,
    ) as job:
        # save
        job.save()
        # run
        job.run()
