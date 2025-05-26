from functools import wraps
from pathlib import Path
from typing import Callable, ParamSpec, TypeVar, cast

import click

from mosaic.utils.time import HMS

P = ParamSpec("P")
R = TypeVar("R")

ToBeWrapped = Callable[P, R]
Wrapped = Callable[P, R | None]
Wrapper = Callable[[ToBeWrapped[P, R], ], Wrapped[P, R]]


def preprocess(func: ToBeWrapped[P, R]) -> Wrapped[P, R]:
    # wrapped function
    @wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R | None:
        # extract
        input_file = cast(Path, kwargs['input_file'])
        start_time = cast(HMS, kwargs['start_time'])
        end_time = cast(HMS, kwargs['end_time'])
        force = cast(bool, kwargs['force'])
        time_tag = cast(bool, kwargs['time_tag'])
        output_file = cast(Path, kwargs['output_file'])

        # verify inputs
        if not input_file.exists():
            click.secho(f'Input file does not exists: -i {input_file}', fg='red')
            return
        if start_time and end_time:
            if not end_time > start_time:
                click.secho(f'Invalid start time or end time: -ss {start_time}, -to {end_time}', fg='red')
                return
        if not force and output_file.exists():
            if click.prompt(
                click.style(f'Output file {output_file} already exist, overwrite? y/[N]', fg='red'),
                type=str,
                default='n',
                show_default=False,
            ).lower() != 'y':
                return

        # modify output filename
        if time_tag:
            output_file = output_file.with_stem(
                f'{output_file.stem}--'
                f'{start_time.time_tag if start_time else ""}-'
                f'{end_time.time_tag if end_time else ""}')

        # remove unwanted args
        kwargs.pop('force')
        kwargs.pop('time_tag')

        # run the actual function, return as is
        return func(*args, **kwargs)

    # return the wrapped function
    return wrapped
