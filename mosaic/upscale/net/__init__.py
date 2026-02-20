from dataclasses import dataclass
from pathlib import Path
from typing import Literal, get_args

from mosaic.upscale.net.rrdb_net import RRDBNet
from mosaic.upscale.net.srvgg_net import SRVGGNetCompact

PACKAGE_DIR = Path(__file__).parent


@dataclass
class Preset:
    model: RRDBNet | SRVGGNetCompact
    scale: int
    filename: str

    @property
    def model_path(self) -> Path:
        return PACKAGE_DIR/f'state_dicts/{self.filename}'


ModelNames = Literal[
    'RealESRGAN_x4plus',
    'RealESRNet_x4plus',
    'RealESRGAN_x4plus_anime_6B',
    'RealESRGAN_x2plus',
    'realesr_animevideov3',
]

PRESETS = get_args(ModelNames)  # to be delete

presets = {k: v for k, v in zip(get_args(ModelNames), (
    Preset(
        # 67 MB
        filename='RealESRGAN_x4plus.pth',
        model=RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=4
        ),
        scale=4,
    ),
    Preset(
        # 67 MB
        filename='RealESRNet_x4plus.pth',
        model=RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=4
        ),
        scale=4,
    ),
    Preset(
        # 17 MB
        filename='RealESRGAN_x4plus_anime_6B.pth',
        model=RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=6,
            num_grow_ch=32,
            scale=4
        ),
        scale=4,
    ),
    Preset(
        # 67 MB
        filename='RealESRGAN_x2plus.pth',
        model=RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=2
        ),
        scale=2,
    ),
    Preset(
        # 2.39 MB
        filename='realesr-animevideov3.pth',
        model=SRVGGNetCompact(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_conv=16,
            upscale=4,
            act_type='prelu',
        ),
        scale=4,
    )
))}

OutputResolution = Literal["720p", "1080p", "1440p", "2160p"]
