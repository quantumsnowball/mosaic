from typing import Literal

from mosaic.utils import ROOT_DIR

JOBS_DIR = ROOT_DIR / 'jobs'

Command = Literal['free', 'lada', 'upscale', 'copy']
