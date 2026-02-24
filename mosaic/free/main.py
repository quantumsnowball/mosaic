from pathlib import Path
from typing import Annotated

import typer
from typer import Argument, Option

from mosaic.utils.logging import log
from mosaic.utils.service import service
from mosaic.utils.time import HMS, parse_hms

from ._args import preprocess_args
from .cleaner import Cleaner
from .net.netG import video
from .net.netM import bisenet

PACKAGE_DIR = Path(__file__).parent


app = typer.Typer()


@app.command(
    no_args_is_help=True,
    help='use DeepMosaics to restore video'
)
@service()
def free(
    output_file: Annotated[Path, Argument(help='Output file path')],
    input_file: Annotated[Path, Option('--input-file', '-i', help='input media path')],
    start_time: Annotated[HMS | None, Option('--start-time', '-ss', parser=parse_hms, help='start time in HH:MM:SS')] = None,
    end_time: Annotated[HMS | None, Option('--end-time', '-to', parser=parse_hms, help='end time in HH:MM:SS')] = None,
    force: Annotated[bool, Option('--force', '-y', help='overwrite output file without asking')] = False,
    time_tag: Annotated[bool, Option('--time-tag', help='auto append time tag at end of filename')] = False,
    raw_info: Annotated[bool, Option('--raw-info', help='display raw ffmpeg info')] = False,
) -> None:
    # preprocess args
    output_file, input_file, start_time, end_time, raw_info = preprocess_args(
        output_file, input_file, start_time, end_time, force, time_tag, raw_info)

    # run
    with Cleaner(
        input_file=input_file,
        start_time=start_time,
        end_time=end_time,
        output_file=output_file,
        raw_info=raw_info,
        netM=bisenet(PACKAGE_DIR/'net/netM/state_dicts/mosaic_position.pth'),
        netG=video(PACKAGE_DIR/'net/netG/state_dicts/clean_youknow_video.pth'),
    ) as cleaner:
        try:
            cleaner.run()
        except KeyboardInterrupt as e:
            log.info(e.__class__)
            cleaner.stop()
