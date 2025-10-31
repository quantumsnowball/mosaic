from pathlib import Path

import click

from mosaic.jobs.job.copy import CopyJob
from mosaic.jobs.job.free import FreeJob
from mosaic.jobs.job.lada import LadaJob
from mosaic.jobs.job.upscale import UpscaleJob
from mosaic.upscale.net import PRESETS
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
    model = click.option(
        '-m',
        '--model',
        default='realesr_animevideov3',
        type=click.Choice(PRESETS),
        help='Real-ESRGAN model choices'
    )
    scale = click.option(
        '-s',
        '--scale',
        default='1080p',
        type=click.Choice(('720p', '1080p', '1440p', '2160p')),
        help='output scale'
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
    with FreeJob.create(
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
def lada(
    input_file: Path,
    segment_time: HMS,
    output_file: Path,
) -> None:
    # create a new job
    with LadaJob.create(
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
    with CopyJob.create(
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
@args.model
@args.scale
@args.output_file
@service()
def upscale(
    input_file: Path,
    segment_time: HMS,
    model: str,
    scale: str,
    output_file: Path,
) -> None:
    # create a new job
    with UpscaleJob.create(
        segment_time=segment_time,
        model=model,
        scale=scale,
        input_file=input_file,
        output_file=output_file,
    ) as job:
        # save
        job.save()
        # run
        job.run()
