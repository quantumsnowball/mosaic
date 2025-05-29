from pathlib import Path

import click

from mosaic.jobs.job import create_job
from mosaic.utils.path import PathParamType
from mosaic.utils.service import service
from mosaic.utils.time import HMS, HMSParamType


@click.group
def create() -> None:
    pass


class args:
    input_file = click.option(
        '-i',
        '--input-file',
        required=True,
        type=PathParamType(),
        help='input media path'
    )
    segment_time = click.option(
        '-sg',
        '--segment-time',
        required=False,
        default='00:05:00',
        type=HMSParamType(),
        help='segment time'
    )
    output_file = click.argument(
        'output-file',
        required=True,
        type=PathParamType()
    )


@create.command
@args.input_file
@args.segment_time
@args.output_file
@service()
def free(
    input_file: Path,
    segment_time: HMS,
    output_file: Path,
) -> None:
    # create a new job
    with create_job(
        command='free',
        segment_time=segment_time,
        input_file=input_file,
        output_file=output_file,
    ) as job:
        # save
        job.save()
        # run
        job.run()


@create.command
@args.input_file
@args.segment_time
@args.output_file
@service()
def copy(
    input_file: Path,
    segment_time: HMS,
    output_file: Path,
) -> None:
    # create a new job
    with create_job(
        command='copy',
        segment_time=segment_time,
        input_file=input_file,
        output_file=output_file,
    ) as job:
        # save
        job.save()
        # run
        job.run()
