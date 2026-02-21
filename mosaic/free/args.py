from pathlib import Path

from rich.prompt import Confirm
from typer import BadParameter, Exit

from mosaic.utils.time import HMS


def preprocess_args(
    output_file: Path,
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    force: bool,
    time_tag: bool,
    raw_info: bool,
) -> tuple[Path, Path, HMS | None, HMS | None, bool]:
    # verify inputs
    if not input_file.exists():
        raise BadParameter(f'Input file does not exists: -i {input_file}')

    # verify time
    if start_time and end_time:
        if not end_time > start_time:
            raise BadParameter(f'Invalid start time or end time: -ss {start_time}, -to {end_time}')

    # modify output filename
    if time_tag:
        output_file = output_file.with_stem(
            f'{output_file.stem}--'
            f'{start_time.time_tag if start_time else ""}-'
            f'{end_time.time_tag if end_time else ""}')

    # prompt for output overwrite
    if not force and output_file.exists():
        if not Confirm.ask(f'[red]Output file {output_file} already exist, overwrite?[/]', default=False):
            raise Exit()

    return output_file, input_file, start_time, end_time, raw_info
