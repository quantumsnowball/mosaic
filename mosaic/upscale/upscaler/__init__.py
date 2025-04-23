import sys
from pathlib import Path
from threading import Event

from mosaic.upscale.net.real_esrgan import RealESRGANer
from mosaic.upscale.upscaler.combiner import Combiner
from mosaic.upscale.upscaler.processor import Processor
from mosaic.upscale.upscaler.source import VideoSource
from mosaic.upscale.upscaler.splitter import Splitter
from mosaic.utils import HMS


def run(
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    output_file: Path,
    upsampler: RealESRGANer,
) -> None:
    # extract video info
    source = VideoSource(input_file, start_time, end_time)

    # processing pipeline
    with (
        Splitter(source) as splitter,
        Processor(splitter, upsampler) as processor,
        Combiner(processor, output_file) as combiner
    ):
        # run
        splitter.run()
        processor.run()
        combiner.run()

        try:
            # wait all procs
            splitter.wait()
            processor.wait()
            combiner.wait()
        except KeyboardInterrupt:
            splitter.stop()
            processor.stop()
            combiner.stop()
