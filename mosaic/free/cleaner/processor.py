import os
from multiprocessing import Process
from pathlib import Path

import numpy as np

from mosaic.free.cleaner.packer import Packer


class Processor:
    output_pipe = Path('/tmp/mosaic-free-processor-output')

    def __init__(self,
                 src: Packer) -> None:
        if not self.output_pipe.exists():
            os.mkfifo(self.output_pipe)
        self._src = src
        self._proc = Process(target=self._worker)

    def _worker(self) -> None:
        with open(self.output_pipe, 'wb') as pipe:
            while True:
                frame = self._src.queue.get()
                if frame is None:
                    break
                out_bytes = frame.astype(np.uint8).tobytes()
                pipe.write(out_bytes)

    def run(self) -> None:
        self._proc.start()

    def wait(self) -> None:
        self._proc.join()
