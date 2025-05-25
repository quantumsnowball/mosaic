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
        pass

    @trace
    def __enter__(self) -> Self:
        return self

    @trace
    def __exit__(self, type, value, traceback) -> None:
        pass

    @trace
    def start(self) -> None:
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
    scale: str,
    output_file: Path,
    raw_info: bool,
    upsampler: RealESRGANer,
) -> None:
    # extract video info
    source = VideoSource(input_file, start_time, end_time)
    dest = VideoDest(output_file, scale)

    # processing pipeline
    with (
        Splitter(source) as splitter,
        Processor(splitter, upsampler) as processor,
        Combiner(processor, dest, raw_info) as combiner
    ):
        # run
        splitter.run()
        processor.run()
        combiner.run()

        def wait() -> None:
            # wait until the last worker
            splitter.wait()
            processor.wait()
            combiner.wait()

        def stop() -> None:
            # stop all workers
            splitter.stop()
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
