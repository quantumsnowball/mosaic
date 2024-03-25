from pathlib import Path

import torch

from mosaic.free.net.netG.BVDNet import define_G as video_G
from mosaic.free.net.netG.BVDNet import show_paramsnumber


def video(model_path: Path):
    netG = video_G(N=2, n_blocks=4)
    show_paramsnumber(netG, 'netG')
    # netG.load_state_dict(torch.load(opt.model_path))
    netG.load_state_dict(torch.load(model_path))
    netG.cuda()
    netG.eval()
    return netG
