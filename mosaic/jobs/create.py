from pathlib import Path
from typing import Annotated

import typer
from typer import Argument, Option

from mosaic.upscale.net import ModelNames, OutputResolution
from mosaic.utils.service import service
from mosaic.utils.time import HMS, parse_hms

from .job.copy import CopyJob
from .job.free import FreeJob
from .job.lada import LadaJob
from .job.upscale import UpscaleJob

app = typer.Typer(no_args_is_help=True, help='create a jobs')


class args:
    input_file = Annotated[Path, Option('--input-file', '-i', help='input media path')]
    segment_time = Annotated[HMS, Option('--segment-time', '-sg', parser=parse_hms, help='segment time')]
    output_file = Annotated[Path, Argument(help='output media path')]
    model = Annotated[ModelNames, Option('--model', '-m', help='Real-ESRGAN model choices')]
    scale = Annotated[OutputResolution, Option('--scale', '-s', help='output scale')]

    class default:
        segment_time: HMS = parse_hms('00:05:00')
        model: ModelNames = 'realesr_animevideov3'
        scale: OutputResolution = '1080p'


@app.command(no_args_is_help=True)
@service()
def free(
    input_file: args.input_file,
    output_file: args.output_file,
    segment_time: args.segment_time = args.default.segment_time,
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


@app.command(no_args_is_help=True)
@service()
def lada(
    input_file: args.input_file,
    output_file: args.output_file,
    segment_time: args.segment_time = args.default.segment_time,
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


@app.command(no_args_is_help=True)
@service()
def copy(
    input_file: args.input_file,
    output_file: args.output_file,
    segment_time: args.segment_time = args.default.segment_time,
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


@app.command(no_args_is_help=True)
@service()
def upscale(
    input_file: args.input_file,
    output_file: args.output_file,
    model: args.model = args.default.model,
    scale: args.scale = args.default.scale,
    segment_time: args.segment_time = args.default.segment_time,
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
