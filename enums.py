from enum import Enum


class PartEnum(Enum):
    BACKCOVER = 0
    PCB = 1
    FUSE = 2
    BLACKCOVER = 3
    WHITECOVER = 4
    BLUECOVER = 5,
    INVALID = 6


class OrientationEnum(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
