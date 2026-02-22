from pathlib import Path
from typing import Annotated, Optional

import typer
from typer import Argument, Option

from mosaic.utils.logging import log
from mosaic.utils.service import service
from mosaic.utils.time import HMS, parse_hms

from ._args import preprocess_args
from .net import ModelNames, OutputResolution, presets
from .net.real_esrgan import RealESRGANer
from .upscaler import Upscaler

PACKAGE_DIR = Path(__file__).parent


app = typer.Typer()


@app.command(no_args_is_help=True)
@service()
def upscale(
    output_file: Annotated[Path, Argument(help='output file path')],
    input_file: Annotated[Path, Option('--input-file', '-i', help='input media path')],
    start_time: Annotated[Optional[HMS], Option('--start-time', '-ss', parser=parse_hms, help='start time in HH:MM:SS')] = None,
    end_time: Annotated[Optional[HMS], Option('--end-time', '-to', parser=parse_hms, help='end time in HH:MM:SS')] = None,
    model: Annotated[ModelNames, Option('--model', '-m', help='Real-ESRGAN model choices')] = 'realesr_animevideov3',
    scale: Annotated[OutputResolution, Option('--scale', '-s', help='output scale')] = '1080p',
    force: Annotated[bool, Option('--force', '-y', help='overwrite output file without asking')] = False,
    raw_info: Annotated[bool, Option('--raw-info', help='display raw ffmpeg info')] = False,
) -> None:
    # preprocess args
    output_file, input_file, start_time, end_time, model, scale, raw_info = preprocess_args(
        output_file, input_file, start_time, end_time, model, scale, force, raw_info)

    # load upsampler
    net = presets[model]
    upsampler = RealESRGANer(
        scale=net.scale,
        model_path=net.model_path,
        model=net.model,
        gpu_id=0,
    )

    with Upscaler(
        input_file=input_file,
        start_time=start_time,
        end_time=end_time,
        output_file=output_file,
        scale=scale,
        raw_info=raw_info,
        upsampler=upsampler,
    ) as upscaler:
        try:
            upscaler.run()
        except KeyboardInterrupt as e:
            log.info(e.__class__)
            upscaler.stop()
