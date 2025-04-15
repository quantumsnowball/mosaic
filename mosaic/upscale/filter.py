import cv2
import numpy as np


def upscale(frame: np.ndarray) -> np.ndarray:
    return frame


def sharpen(frame: np.ndarray) -> np.ndarray:
    # Define the sharpening kernel
    sharpening_kernel = np.array([[0, -1, 0],
                                  [-1, 5, -1],
                                  [0, -1, 0]])

    # Apply the sharpening filter using filter2D
    sharpened_frame = cv2.filter2D(frame, -1, sharpening_kernel)
    return sharpened_frame
