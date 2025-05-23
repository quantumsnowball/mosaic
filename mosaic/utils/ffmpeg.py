from subprocess import Popen
from typing import Self


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

    def global_args(self, *args: str, at: int | None = None) -> Self:
        if at is None:
            at = len(self._global_args)
        for arg in reversed(args):
            self._global_args.insert(at, arg)
        return self

    def input(self, *args: str, at: int | None = None) -> Self:
        if at is None:
            at = len(self._input)
        for arg in reversed(args):
            self._input.insert(at, arg)
        return self

    def output(self, *args: str, at: int | None = None) -> Self:
        if at is None:
            at = len(self._output)
        for arg in reversed(args):
            self._output.insert(at, arg)
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
    ff.global_args('-hide_banner', at=1)
    print(ff)
