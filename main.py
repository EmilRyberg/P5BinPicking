from utils import Utils
NUMBER_OF_PARTS = 4
BIG_GRIPPER = 0
SUCTION = 1
SMALL_GRIPPER = 2
FINAL_COVER = 3

class Controller():
    def __init__(self):
        self.in_zero_position = False
        self.part_id = None
        self.colour_id = None
        self.location = None
        self.orientation = None
        self.utils = Utils()
        print("[I] Controller running")

    def main_flow(self, colour_id):
        if not self.in_zero_position:
            self.move_arm(0.0, 0.0) #Move to zero position
            self.in_zero_position = True
        for i in range(0, NUMBER_OF_PARTS-1): #leaving front cover out for later choice of colour
            self.part_id=i
            position, orientation = self.get_part_location(self.part_id)
            self.move_arm(position, orientation)
            self.pick_up(self.part_id)
            self.place_part(self.part_id)
        position, orientation = self.get_part_location(self.colour_id) #3: black, 4: white, 5: blue
        self.move_arm(position, orientation)
        self.pick_up(self.colour_id)
        self.place_part(self.colour_id)

    def pick_up(self, part_id):
        if part_id == 0:
            tool = "big gripper"
            print("[I] big gripper to pick up ", self.utils.part_id_to_name(part_id))
        elif part_id == 1:
            tool = "suction"
            print("[I] using suction to pick up ", self.utils.part_id_to_name(part_id))
        elif part_id == 2:
            tool = "small gripper"
            print("[I] using small gripper to pick up ", self.utils.part_id_to_name(part_id))
        elif 2 < part_id < 6:
            tool = "big gripper"
            print("[I] big gripper to pick up ", self.utils.part_id_to_name(part_id))
        else:
            print("[WARNING] wrong part. ID recieved: ", part_id)
            return

    def place_part(self, part_id):
        if part_id==0:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        elif part_id==1:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        elif part_id==2:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        elif 2 < part_id < 6:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        else:
            print("[WARNING] wrong part. ID recieved: ", part_id)

    def move_arm(self, position, orientation):
        print("[I] Moving arm")
        self.in_zero_position = False

    def get_part_location(self, part_id):
        location = (10.5, 20.1)
        orientation = 1
        return location, orientation

controller = Controller()

while True:
    print("Please write a command (write 'help' for a list of commands):")
    command = input()
    if command == "help":
        print("Possible commands are: \nblack: assemble phone with black cover \nwhite: assemble phone with white cover \n"
            "blue: assemble phone with blue cover \nzero: put the robot in zero position \nquit: close the program")
    elif command == "black":
        controller.colour_id = 3
        controller.main_flow(controller.colour_id)
    elif command == "white":
        controller.colour_id = 4
        controller.main_flow(controller.colour_id)
    elif command == "blue":
        controller.colour_id = 5
        controller.main_flow(controller.colour_id)
    elif command == "zero":
        controller.move_arm(0,0)
    elif command == "quit":
        break
    else:
        print("Invalid command, please try again")


