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
        pass

    @trace
    def __enter__(self) -> Self:
        return self

    @trace
    def __exit__(self, type, value, traceback) -> None:
        pass

    @trace
    def run(self) -> None:
        pass

    @trace
    def wait(self) -> None:
        pass

    @trace
    def stop(self) -> None:
        pass


@trace
def run(
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    output_file: Path,
    raw_info: bool,
    netM: BiSeNet,
    netG: BVDNet,
) -> None:
    # extract video info
    source = VideoSource(input_file, start_time, end_time)

    # processing pipeline
    with (
        Splitter(source) as splitter,
        Packer(splitter) as packer,
        Processor(packer, netM=netM, netG=netG) as processor,
        Combiner(processor, output_file, raw_info) as combiner
    ):
        # run
        splitter.run()
        packer.run()
        processor.run()
        combiner.run()

        def wait() -> None:
            # wait until the last worker
            splitter.wait()
            packer.wait()
            processor.wait()
            combiner.wait()

        def stop() -> None:
            # stop all workers
            splitter.stop()
            packer.stop()
            processor.stop()
            combiner.stop()

        try:
            # wait for all workers
            wait()
        except KeyboardInterrupt:
            # upon kbint, only stop splitter
            stop()
            # raise again
            raise
        finally:
            # wait for all workers again
            wait()
