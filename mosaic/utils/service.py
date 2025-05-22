from contextlib import ContextDecorator
from typing import Self

from mosaic.utils import ROOT_DIR, TEMP_DIR


class service(ContextDecorator):
    def __enter__(self) -> Self:
        ROOT_DIR.mkdir(exist_ok=True)
        TEMP_DIR.mkdir(exist_ok=True)
        return self

    def __exit__(self, *_) -> None:
        try:
            TEMP_DIR.rmdir()
            ROOT_DIR.rmdir()
        except OSError:
            pass
