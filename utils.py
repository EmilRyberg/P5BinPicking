class Utils():
    def __init__(self):
        self.part_id = 0
    def part_id_to_name(self, part_id):
        if part_id == 0:
            return "Back cover"
        elif part_id == 1:
            return "PCB"
        elif part_id == 2:
            return "Fuse"
        elif part_id == 3:
            return "Black front cover"
        elif part_id == 4:
            return "White front cover"
        elif part_id == 5:
            return "Blue front cover"
