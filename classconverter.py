from vision import Vision
from part_enum import PartEnum

class ClassConverter:
    def convert_part_id(part_id):
        if part_id == PartEnum.FUSE.value:
            return ('Fuse', 'Fuse')
        elif part_id == PartEnum.BACKCOVER.value:
            return ('BottomCover', 'BottomCoverFlipped')
        elif part_id == PartEnum.WHITECOVER.value:
            return ('WhiteCover', 'WhiteCoverFlipped')
        elif part_id == PartEnum.BLUECOVER.value:
            return ('BlueCover', 'BlueCoverFlipped')
        elif part_id == PartEnum.BLACKCOVER.value:
            return ('BlackCover', 'BlackCoverFlipped')
        elif part_id == PartEnum.PCB.value:
            return ('PCB', 'PCBFlipped')
        else:
            print("[W] Could not convert class_id")
            return (-1, -1)




