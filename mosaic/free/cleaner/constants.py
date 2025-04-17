import numpy as np

N, T, S = 2, 5, 3
LEFT_FRAME = (N*S)         # 6
POOL_NUM = LEFT_FRAME*2+1  # 13
INPUT_SIZE = 256
FRAME_POS = np.linspace(0, (T-1)*S, T, dtype=np.int64)
