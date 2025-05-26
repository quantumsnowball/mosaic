from pathlib import Path

import click

PACKAGE_ROOT = Path(__file__).parent.parent
ROOT_DIR = Path('.mosaic')
TEMP_DIR = ROOT_DIR / '.temp'


class VideoPathParamType(click.ParamType):
    name = 'VideoPath'

    def convert(self,
                value: str,
                param: click.Parameter | None,
                ctx: click.Context | None) -> Path:
        return Path(value)
