from pathlib import Path

from rich.prompt import Confirm
from typer import BadParameter, Exit


def preprocess_args(
    output_file: Path,
    input_file: Path,
    force: bool,
) -> tuple[Path, Path]:
    # verify inputs
    if not input_file.exists():
        raise BadParameter(f'Input file does not exists: -i {input_file}')

    # prompt for output overwrite
    if not force and output_file.exists():
        if not Confirm.ask(f'[red]Output file {output_file} already exist, overwrite?[/]', default=False,):
            raise Exit()

    return output_file, input_file
