from pathlib import Path

import torch

from mosaic.free.net.netM.BiSeNet import BiSeNet, show_paramsnumber


def bisenet(model_path: Path) -> BiSeNet:
    net = BiSeNet(num_classes=1,
                  context_path='resnet18',
                  train_flag=False)
    show_paramsnumber(net, 'segment')
    # if type == 'roi':
    #     net.load_state_dict(torch.load(opt.model_path))
    # elif type == 'mosaic':
    #     net.load_state_dict(torch.load(opt.mosaic_position_model_path))
    net.load_state_dict(torch.load(model_path))
    # net = todevice(net, opt.gpu_id)
    net.cuda()
    net.eval()
    return net
