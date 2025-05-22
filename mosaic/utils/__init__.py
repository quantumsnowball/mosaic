import re
import shutil
from pathlib import Path

import click

ROOT_DIR = Path('.mosaic')
TEMP_DIR = ROOT_DIR / '.temp'


class HMS:
    def __init__(self,
                 hours: int,
                 minutes: int,
                 seconds: int):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def total_seconds(self) -> int:
        return self.hours * 3600 + self.minutes * 60 + self.seconds

    def __gt__(self, other: 'HMS') -> bool:
        return self.total_seconds() > other.total_seconds()

    def __lt__(self, other: 'HMS') -> bool:
        return self.total_seconds() < other.total_seconds()

    def __int__(self) -> int:
        return self.total_seconds()

    def __sub__(self, other: 'HMS') -> 'HMS':
        total_seconds = self.total_seconds() - other.total_seconds()

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = (total_seconds % 3600) % 60

        return HMS(hours, minutes, seconds)

    def __str__(self) -> str:
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"

    @property
    def time_tag(self) -> str:
        return f"{self.hours:02d}{self.minutes:02d}{self.seconds:02d}"


class HMSParamType(click.ParamType):
    name = 'HMS'
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$')

    def convert(self,
                value: str,
                param: click.Parameter | None,
                ctx: click.Context | None) -> HMS:
        if not self.time_pattern.match(value):
            self.fail('Invalid time format. Please provide time in HH:MM:SS format.')
        hours, minutes, seconds = map(int, value.split(':'))
        return HMS(hours, minutes, seconds)


class VideoPathParamType(click.ParamType):
    name = 'VideoPath'

    def convert(self,
                value: str,
                param: click.Parameter | None,
                ctx: click.Context | None) -> Path:
        return Path(value)
