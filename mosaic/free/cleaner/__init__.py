from contextlib import ExitStack
from pathlib import Path
from typing import Self

from mosaic.free.cleaner.combiner import Combiner
from mosaic.free.cleaner.packer import Packer
from mosaic.free.cleaner.processor import Processor
from mosaic.free.cleaner.splitter import Splitter
from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.utils import HMS
from mosaic.utils.logging import trace
from mosaic.utils.spec import VideoSource


class Cleaner:
    def __init__(
        self,
        input_file: Path,
        start_time: HMS | None,
        end_time: HMS | None,
        output_file: Path,
        raw_info: bool,
        netM: BiSeNet,
        netG: BVDNet,
    ) -> None:
        source = VideoSource(input_file, start_time, end_time)
        self.splitter = Splitter(source)
        self.packer = Packer(self.splitter)
        self.processor = Processor(self.packer, netM=netM, netG=netG)
        self.combiner = Combiner(self.processor, output_file, raw_info)
        self.cm = ExitStack()

    @trace
    def __enter__(self) -> Self:
        self.cm.enter_context(self.splitter)
        self.cm.enter_context(self.packer)
        self.cm.enter_context(self.processor)
        self.cm.enter_context(self.combiner)
        return self

    @trace
    def __exit__(self, type, value, traceback) -> None:
        self.wait()
        self.cm.close()

    @trace
    def start(self) -> None:
        self.splitter.start()
        self.packer.start()
        self.processor.start()
        self.combiner.start()

    @trace
    def run(self) -> None:
        self.start()
        self.wait()

    @trace
    def wait(self) -> None:
        self.splitter.wait()
        self.packer.wait()
        self.processor.wait()
        self.combiner.wait()

    @trace
    def stop(self) -> None:
        self.splitter.stop()
        self.packer.stop()
        self.processor.stop()
        self.combiner.stop()
