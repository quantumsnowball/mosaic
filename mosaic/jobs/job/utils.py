from pathlib import Path

from rich.prompt import Confirm


def prompt_overwrite_output(output_file: Path) -> bool:
    # output_file already exists
    if output_file.exists():
        if not Confirm.ask(f'[red]Output file {output_file} already exist, overwrite?[/]', default=False):
            # stop the overwrite
            return False

    # default is safe to overwrite
    return True
