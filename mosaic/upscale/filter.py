import numpy as np


def upscale_filter(frame: np.ndarray) -> np.ndarray:
    frame = 255 - frame
    return frame
