import numpy as np
import math
from enums import PartEnum


def rpy_to_rot_vect(r, p, y):
    r = math.radians(r)
    p = math.radians(p)
    y = math.radians(y)

    yaw_matrix = np.array([
        [math.cos(y), -math.sin(y), 0],
        [math.sin(y), math.cos(y), 0],
        [0, 0, 1]
    ], dtype=np.float32)

    pitch_matrix = np.array([
        [math.cos(p), 0, math.sin(p)],
        [0, 1, 0],
        [-math.sin(p), 0, math.cos(p)]
    ], dtype=np.float32)

    roll_matrix = np.array([
        [1, 0, 0],
        [0, math.cos(r), -math.sin(r)],
        [0, math.sin(r), math.cos(r)]
    ], dtype=np.float32)

    R = yaw_matrix * pitch_matrix * roll_matrix

    theta = math.acos(((R[0, 0] + R[1, 1] + R[2, 2]) - 1) / 2)
    multi = 1 / (2 * math.sin(theta))

    rx = multi * (R[2, 1] - R[1, 2]) * theta
    ry = multi * (R[0, 2] - R[2, 0]) * theta
    rz = multi * (R[1, 0] - R[0, 1]) * theta
    return [rx, ry, rz]


def part_id_to_name(self, part_id):
    if part_id == PartEnum.BACKCOVER.value:
        return "Back cover"
    elif part_id == PartEnum.PCB.value:
        return "PCB"
    elif part_id == PartEnum.FUSE.value:
        return "Fuse"
    elif part_id == PartEnum.BLACKCOVER.value:
        return "Black front cover"
    elif part_id == PartEnum.WHITECOVER.value:
        return "White front cover"
    elif part_id == PartEnum.BLUECOVER.value:
        return "Blue front cover"
