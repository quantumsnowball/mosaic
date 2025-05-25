from contextlib import ExitStack
from pathlib import Path
from typing import Self

from mosaic.upscale.net.real_esrgan import RealESRGANer
from mosaic.upscale.upscaler.combiner import Combiner
from mosaic.upscale.upscaler.processor import Processor
from mosaic.upscale.upscaler.splitter import Splitter
from mosaic.utils import HMS
from mosaic.utils.logging import trace
from mosaic.utils.spec import VideoDest, VideoSource


class Upscaler:
    def __init__(
        self,
        input_file: Path,
        start_time: HMS | None,
        end_time: HMS | None,
        scale: str,
        output_file: Path,
        raw_info: bool,
        upsampler: RealESRGANer,
    ) -> None:
        source = VideoSource(input_file, start_time, end_time)
        dest = VideoDest(output_file, scale)
        self.splitter = Splitter(source)
        self.processor = Processor(self.splitter, upsampler)
        self.combiner = Combiner(self.processor, dest, raw_info)
        self.cm = ExitStack()

    @trace
    def __enter__(self) -> Self:
        self.cm.enter_context(self.splitter)
        self.cm.enter_context(self.processor)
        self.cm.enter_context(self.combiner)
        return self

    @trace
    def __exit__(self, type, value, traceback) -> None:
        self.wait()
        self.cm.close()

    @trace
    def start(self) -> None:
        self.splitter.run()
        self.processor.run()
        self.combiner.run()

    @trace
    def run(self) -> None:
        self.start()
        self.wait()

    @trace
    def wait(self) -> None:
        self.splitter.wait()
        self.processor.wait()
        self.combiner.wait()

    @trace
    def stop(self) -> None:
        self.splitter.stop()
        self.processor.stop()
        self.combiner.stop()
