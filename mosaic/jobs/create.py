from pathlib import Path
from typing import Annotated

import click
import typer
from typer import Argument, Option

from mosaic.jobs.job.copy import CopyJob
from mosaic.jobs.job.free import FreeJob
from mosaic.jobs.job.lada import LadaJob
from mosaic.jobs.job.upscale import UpscaleJob
from mosaic.upscale.net import PRESETS, ModelNames, OutputResolution
from mosaic.utils.path import PathParamType
from mosaic.utils.service import service
from mosaic.utils.time import HMS, HMSParamType, parse_hms

app = typer.Typer(no_args_is_help=True, help="create a jobs")


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


class Args:
    input_file = Annotated[Path, Option("--input-file", "-i", help="input media path")]
    segment_time = Annotated[HMS, Option("--segment-time", "-sg", parser=parse_hms, help="segment time")]
    output_file = Annotated[Path, Argument(help="output media path")]
    model = Annotated[ModelNames, Option("--model", "-m", help='Real-ESRGAN model choices')]
    scale = Annotated[OutputResolution, Option("--scale", "-s", help="output scale")]

    class default:
        segment_time = parse_hms('00:05:00')


@app.command()
@service()
def free(
    input_file: Args.input_file,
    output_file: Args.output_file,
    segment_time: Args.segment_time = Args.default.segment_time,
) -> None:
    # create a new job
    with FreeJob.create(
        segment_time=segment_time,
        input_file=input_file,
        output_file=output_file,
    ) as job:
        # save
        job.save()
        # initialize
        job.initialize()


@app.command()
@service()
def lada(
    input_file: Args.input_file,
    output_file: Args.output_file,
    segment_time: Args.segment_time = Args.default.segment_time,
) -> None:
    # create a new job
    with LadaJob.create(
        segment_time=segment_time,
        input_file=input_file,
        output_file=output_file,
    ) as job:
        # save
        job.save()
        # initialize
        job.initialize()


@app.command()
@service()
def copy(
    input_file: Args.input_file,
    output_file: Args.output_file,
    segment_time: Args.segment_time = Args.default.segment_time,
) -> None:
    # create a new job
    with CopyJob.create(
        segment_time=segment_time,
        input_file=input_file,
        output_file=output_file,
    ) as job:
        # save
        job.save()
        # initialize
        job.initialize()


# @create.command
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
        # initialize
        job.initialize()
