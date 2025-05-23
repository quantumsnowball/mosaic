from subprocess import Popen
from typing import Any, Self


class FFmpeg:
    _command = ['ffmpeg', ]

    def __init__(self) -> None:
        self._global_args: list[str] = []
        self._input: list[str] = []
        self._output: list[str] = []

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
    def _insert_to(target: list[str], *args: Any, at: int | None = None) -> None:
        # try to convert every arg to str
        str_args = list(map(str, args))

        try:
            # on correct index value, try insert args at that index position
            assert isinstance(at, int)
            target[at:at] = str_args
        except Exception:
            # default is to extend all args to target's end
            target.extend(str_args)

    def global_args(self, *args: Any, at: int | None = None) -> Self:
        self._insert_to(self._global_args, *args, at=at)
        return self

    def input(self, *args: Any, at: int | None = None) -> Self:
        self._insert_to(self._input, *args, at=at)
        return self

    def output(self, *args: Any, at: int | None = None) -> Self:
        self._insert_to(self._output, *args, at=at)
        return self

    def run_async(self) -> Popen:
        return Popen(self.args)

    def run(self) -> int:
        return self.run_async().wait()
