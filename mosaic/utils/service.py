from contextlib import ContextDecorator
from typing import Self

from mosaic.utils import ROOT_DIR, TEMP_DIR


class service(ContextDecorator):
    def __init__(
        self,
        *,
        mkdir: bool = True,
        rmdir: bool = True,
    ) -> None:
        super().__init__()
        self.mkdir = mkdir
        self.rmdir = rmdir

    def __enter__(self) -> Self:
        if self.mkdir:
            ROOT_DIR.mkdir(exist_ok=True)
            TEMP_DIR.mkdir(exist_ok=True)
        return self

    def __exit__(self, *_) -> None:
        if self.rmdir:
            print('service: do rmdir')
            try:
                TEMP_DIR.rmdir()
            except OSError:
                pass
            try:
                ROOT_DIR.rmdir()
            except OSError:
                pass
