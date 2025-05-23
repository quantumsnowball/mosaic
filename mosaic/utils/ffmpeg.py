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

    def run_async(self) -> Popen:
        return Popen(self.args)

    def run(self) -> int:
        return self.run_async().wait()
