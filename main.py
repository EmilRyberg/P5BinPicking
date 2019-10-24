from utils import Utils
from move_robot import MoveRobot
from vision import Vision
from part_enum import PartEnum
from classconverter import ClassConverter

NUMBER_OF_PARTS = 4
BIG_GRIPPER = 0
SUCTION = 1
SMALL_GRIPPER = 2
FINAL_COVER = 3
FIXTURE_X = 20
FIXTURE_Y = 15


class Controller():
    def __init__(self):
        self.in_zero_position = False
        self.part_id = None
        self.colour_id = None
        self.location = None
        self.orientation = None
        self.utils = Utils()
        self.move_robot = MoveRobot()
        self.vision = Vision()

        print("[I] Controller running")

    def main_flow(self, colour_id):
        if not self.in_zero_position:
            self.move_robot.move_to_zero() #Move to zero position
            self.in_zero_position = True
        for i in range(0, NUMBER_OF_PARTS-1): #leaving front cover out for later choice of colour
            self.part_id=i
            x, y, orientation = self.get_part_location(self.part_id)
            #print("[D]: Position: ", position, " orientation = ", orientation)
            self.move_arm(x, y, orientation, self.part_id)
            #self.pick_up(self.part_id)
            self.place_part(self.part_id)
        x, y, orientation = self.get_part_location(self.colour_id) #3: black, 4: white, 5: blue
        self.move_arm(x, y, orientation, self.colour_id)
        #self.pick_up(self.colour_id)
        self.place_part(self.colour_id)

    """def pick_up(self, part_id):
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
            return"""

    def place_part(self, part_id):
        if part_id == 0:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        elif part_id == 1:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        elif part_id == 2:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        elif 2 < part_id < 6:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        else:
            print("[WARNING] wrong part. ID recieved: ", part_id)
        self.move_robot.place(FIXTURE_X, FIXTURE_Y, part_id)

    def move_arm(self, x, y, orientation, part_id):
        print("[I] Moving arm")
        self.move_robot.grip(x, y, orientation, part_id)
        self.in_zero_position = False

    def get_part_location(self, part_id):
        x, y, orientation = self.vision.detect_object(ClassConverter.convert_part_id(part_id))
        return x, y, orientation


controller = Controller()

while True:
    print("Please write a command (write 'help' for a list of commands):")
    command = input()
    if command == "help":
        print("Possible commands are: \nblack: assemble phone with black cover \nwhite: assemble phone with white cover \n"
            "blue: assemble phone with blue cover \nzero: put the robot in zero position \nquit: close the program")
    elif command == "black":
        controller.colour_id = PartEnum.BLACKCOVER
        controller.main_flow(controller.colour_id)
    elif command == "white":
        controller.colour_id = PartEnum.WHITECOVER
        controller.main_flow(controller.colour_id)
    elif command == "blue":
        controller.colour_id = PartEnum.BLUECOVER
        controller.main_flow(controller.colour_id)
    elif command == "zero":
        controller.move_arm(0, 0)
    elif command == "quit":
        break
    else:
        print("Invalid command, please try again")