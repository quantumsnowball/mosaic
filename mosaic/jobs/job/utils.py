from pathlib import Path

import click


def prompt_overwrite_output(output_file: Path) -> bool:
    # output_file already exists
    if output_file.exists():
        # and user do not agree to overwrite it
        if click.prompt(
            click.style(f'Output file {output_file} already exist, overwrite? y/[N]', fg='red'),
            type=str,
            default='n',
            show_default=False,
        ).lower() != 'y':
            # stop the overwrite
            return False

    # default is safe to overwrite
    return True
