import subprocess
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
        netD_path: Path,
        netR_path: Path,
    ) -> None:
        source = VideoSource(input_file, start_time, end_time)
        self._input_file = input_file
        self._output_file = output_file
        self._netD_path = netD_path
        self._netR_path = netR_path
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
        subprocess.run([
            'lada-cli',
            '--mosaic-restoration-model', 'basicvsrpp',
            '--mosaic-detection-model-path', self._netD_path,
            '--mosaic-restoration-model-path', self._netR_path,
            '--input', self._input_file,
            '--output', self._output_file,
        ], text=True)

    @trace
    def run(self) -> None:
        self.start()
        self.wait()

    @trace
    def wait(self) -> None:
        pass

    @trace
    def stop(self) -> None:
        pass
