from vision import Vision
from part_enum import PartEnum

class ClassConverter():
    def convert_part_id(self, part_id):
        if part_id == PartEnum.FUSE:
            return 0
        elif part_id == PartEnum.BACKCOVER:
            return (1, 2)
        elif part_id == PartEnum.WHITECOVER:
            return (3, 4)
        elif part_id == PartEnum.BLUECOVER:
            return (5, 6)
        elif part_id == PartEnum.BLACKCOVER:
            return (7, 8)
        elif part_id == PartEnum.PCB:
            return (9, 10)
        else:
            print("[W] Could not convert class_id")




