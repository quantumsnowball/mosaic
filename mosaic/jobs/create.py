from pathlib import Path
from typing import Literal

import click

from mosaic.jobs.job import Job
from mosaic.utils import VideoPathParamType
from mosaic.utils.service import service
from mosaic.utils.time import HMS, HMSParamType

CommandName = Literal['free', 'upscale']


@click.group
def create() -> None:
    pass


def make_command(name: CommandName) -> click.Command:
    @create.command(name=name)
    @click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
    @click.option('-sg', '--segment-time', required=False, default='00:05:00', type=HMSParamType(), help='segment time')
    @click.argument('output-file', required=True, type=VideoPathParamType())
    @service()
    def command(
        input_file: Path,
        segment_time: HMS,
        output_file: Path,
    ) -> None:
        # create a new job
        with Job.create(
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
