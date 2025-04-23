from pathlib import Path

from mosaic.free.cleaner.combiner import Combiner
from mosaic.free.cleaner.packer import Packer
from mosaic.free.cleaner.processor import Processor
from mosaic.free.cleaner.source import VideoSource
from mosaic.free.cleaner.splitter import Splitter
from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.utils import HMS


def run(
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    output_file: Path,
    netM: BiSeNet,
    netG: BVDNet,
):
    # extract video info
    source = VideoSource(input_file, start_time, end_time)

    # processing pipeline
    with (
        Splitter(source) as splitter,
        Packer(splitter) as packer,
        Processor(packer, netM=netM, netG=netG) as processor,
        Combiner(processor, output_file) as combiner
    ):
        # run
        splitter.run()
        packer.run()
        processor.run()
        combiner.run()

        # wait all procs
        splitter.wait()
        packer.wait()
        processor.wait()
        combiner.wait()
