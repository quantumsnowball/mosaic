import re
from typing import Self

from typer import BadParameter


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

    @classmethod
    def from_str(cls, txt: str) -> Self:
        h, m, s = map(int, txt.split(':'))
        return cls(h, m, s)

    @classmethod
    def from_total_seconds(cls, total_seconds: int) -> Self:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = (total_seconds % 3600) % 60

        return cls(hours, minutes, seconds)


def parse_hms(value: HMS | str) -> HMS:
    if isinstance(value, HMS):
        return value
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$')
    if not time_pattern.match(value):
        raise BadParameter('Invalid time format. Please provide time in HH:MM:SS format.')
    hours, minutes, seconds = map(int, value.split(':'))
    return HMS(hours, minutes, seconds)
