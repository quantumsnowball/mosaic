from pathlib import Path

import click

from mosaic.jobs.job import create_job
from mosaic.jobs.utils import Command
from mosaic.utils.path import PathParamType
from mosaic.utils.service import service
from mosaic.utils.time import HMS, HMSParamType


@click.group
def create() -> None:
    pass


def make_command(name: Command) -> click.Command:
    @create.command(name=name)
    @click.option('-i', '--input-file', required=True, type=PathParamType(), help='input media path')
    @click.option('-sg', '--segment-time', required=False, default='00:05:00', type=HMSParamType(), help='segment time')
    @click.argument('output-file', required=True, type=PathParamType())
    @service()
    def command(
        input_file: Path,
        segment_time: HMS,
        output_file: Path,
    ) -> None:
        # create a new job
        with create_job(
            command=name,
            segment_time=segment_time,
            input_file=input_file,
            output_file=output_file,
        ) as job:
            # save
            job.save()
            # run
            job.run()

    return command


# free
make_command('free')
make_command('copy')
