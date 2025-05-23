from functools import wraps
from subprocess import Popen
from typing import Callable, Self


class FFmpeg:
    _command = ['ffmpeg', ]

    def __init__(self) -> None:
        self._global_args = []
        self._input = []
        self._output = []

    @property
    def args(self) -> list[str]:
        args = (
            self._command +
            self._global_args +
            self._input +
            self._output
        )
        return args

    def __str__(self) -> str:
        return ' '.join(self.args)

    @staticmethod
    def _insert_to(target: list[str], *args, at: int | None = None) -> None:
        try:
            # on correct index value, try insert args at that index position
            assert isinstance(at, int)
            target[at:at] = args
        except Exception:
            # default is to extend all args to target's end
            target.extend(args)

    def global_args(self, *args: str, at: int | None = None) -> Self:
        self._insert_to(self._global_args, *args, at=at)
        return self

    def input(self, *args: str, at: int | None = None) -> Self:
        self._insert_to(self._input, *args, at=at)
        return self

    def output(self, *args: str, at: int | None = None) -> Self:
        self._insert_to(self._output, *args, at=at)
        return self

    def run(self, *args, **kwargs) -> Popen:
        return Popen(self.args, *args, **kwargs)


if __name__ == "__main__":

    ff = (
        FFmpeg()
        .global_args(
            '-y',
            '-loglevel', 'fatal',
        )
        .input(
            '-i', 'input.mp4',
        )
        .output(
            '-map', '0:v:0',
            '-c', 'copy',
            'output.mp4',
        )
    )
    print(ff)
    ff.global_args(
        '-hide_banner',
        '-abc', 'abc',
        at=-2,
    )
    print(ff)
