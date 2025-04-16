from pathlib import Path

import ffmpeg
import numpy as np

from mosaic.free.cleaner import runmodel
from mosaic.free.cleaner.combiner import Combiner
from mosaic.free.cleaner.packer import Packer
from mosaic.free.cleaner.processor import Processor
from mosaic.free.cleaner.splitter import Splitter
from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.utils import HMS


def run(
    input_file: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    output_file: Path,
    netG: BVDNet,
    netM: BiSeNet
):
    # extract first video stream info
    ffprobe_info = ffmpeg.probe(str(input_file))
    for stream in ffprobe_info['streams']:
        if stream['codec_type'] == 'video':
            width = int(stream['width'])
            height = int(stream['height'])
            framerate = str(stream['r_frame_rate'])
            frame_size = width * height * 3
            break
    else:
        raise ValueError("No video stream found.")

    # ffmpeg input and output procs
    input_kwargs = {k: v
                    for k, v in dict(ss=start_time, to=end_time).items()
                    if v is not None}

    with (
        Splitter(input_file,
                 **input_kwargs) as splitter,

        Packer(splitter,
               width=width,
               height=height,
               maxsize=1) as packer,

        Processor(packer) as processor,
        Combiner(processor,
                 input_file,
                 output_file,
                 width=width,
                 height=height,
                 framerate=framerate,
                 **input_kwargs) as combiner
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
