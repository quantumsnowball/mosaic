from pathlib import Path

from mosaic.free.net.netG.BVDNet import BVDNet
from mosaic.free.net.netM.BiSeNet import BiSeNet
from mosaic.utils import HMS


def clean_mosaic(
    media_path: Path,
    start_time: HMS | None,
    end_time: HMS | None,
    output_file: Path,
    netG: BVDNet,
    netM: BiSeNet
):
    # do all stuffs here
    print('use this clean_mosaic() fucntion here to do all the staff')
