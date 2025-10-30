from contextlib import ExitStack
from pathlib import Path
from typing import Self

from mosaic.utils.logging import trace
from mosaic.utils.spec import VideoSource
from mosaic.utils.time import HMS


class Cleaner:
    def __init__(
        self,
        input_file: Path,
        start_time: HMS | None,
        end_time: HMS | None,
        output_file: Path,
        raw_info: bool,
    ) -> None:
        source = VideoSource(input_file, start_time, end_time)
        self.cm = ExitStack()

    @trace
    def __enter__(self) -> Self:
        return self

    @trace
    def __exit__(self, type, value, traceback) -> None:
        self.wait()
        self.cm.close()

    @trace
    def start(self) -> None:
        print('gonna start cleaner')

    @trace
    def run(self) -> None:
        self.start()
        self.wait()

    @trace
    def wait(self) -> None:
        print('wait for other workers')

    @trace
    def stop(self) -> None:
        print('stop other workers')
