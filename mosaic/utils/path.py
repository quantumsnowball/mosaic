from pathlib import Path

import click


class VideoPathParamType(click.ParamType):
    name = 'VideoPath'

    def convert(self,
                value: str,
                param: click.Parameter | None,
                ctx: click.Context | None) -> Path:
        return Path(value)
