import math
import sys

from numba import jit

FLOAT_MIN = sys.float_info.min


@jit(nopython=True)
def safe_tan(angle):
    # Some small epsilon value
    epsilon = 1e-10

    # Ensure the angle is within [0, 2*pi]
    angle = angle % (2 * math.pi)

    # Check if angle is close (k * pi) and adjust it accordingly
    for k in range(-10, 10):
        critical_value = k * math.pi
        if abs(angle - critical_value) < epsilon:
            angle += FLOAT_MIN

    return angle
