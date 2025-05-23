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

    def _insert_args(self, target: list[str], *args, at: int | None = None) -> None:
        if at is None:
            target += args
        else:
            assert 0 <= at < len(target)
            for arg in reversed(args):
                target.insert(at, arg)

    def global_args(self, *args: str, at: int | None = None) -> Self:
        self._insert_args(self._global_args, *args, at=at)
        return self

    def input(self, *args: str, at: int | None = None) -> Self:
        self._insert_args(self._input, *args, at=at)
        return self

    def output(self, *args: str, at: int | None = None) -> Self:
        self._insert_args(self._output, *args, at=at)
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
        at=1,
    )
    print(ff)
