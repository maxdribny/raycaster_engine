import math


def distance_two_points(a_x, a_y, b_x, b_y):
    return math.sqrt(((b_x - a_x) * (b_x - a_x) + (b_y - a_y) * (b_y - a_y)))
