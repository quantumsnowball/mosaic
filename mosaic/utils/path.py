from pathlib import Path

import click


class PathParamType(click.ParamType):
    name = 'Path'

    def convert(self,
                value: str,
                param: click.Parameter | None,
                ctx: click.Context | None) -> Path:
        return Path(value)
