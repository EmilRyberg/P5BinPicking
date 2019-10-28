from utils import Utils
from move_robot import MoveRobot
from vision import Vision
from part_enum import PartEnum
from classconverter import ClassConverter
from aruco import Calibration
from PIL import Image as pimg
import numpy as np

NUMBER_OF_PARTS = 4
FIXTURE_X = 255
FIXTURE_Y = -320


class Controller:
    def __init__(self):
        self.in_zero_position = False
        self.part_id = None
        self.colour_id = None
        self.location = None
        self.orientation = None
        self.np_image = None
        self.utils = Utils()
        self.move_robot = MoveRobot("192.168.1.148")
        self.vision = Vision()
        self.aruco = Calibration()

        print("[I] Controller running")

    def main_flow(self, colour_id):
        if not self.in_zero_position:
            self.move_robot.move_out_of_view() #Move to zero position
            self.in_zero_position = True
        self.vision.capture_image()
        pil_image = pimg.open("/home/rob/Desktop/P5BinPicking/DarkNet/webcam_capture.png")
        self.np_image = np.array(pil_image)
        """for i in range(NUMBER_OF_PARTS-1): #leaving front cover out for later choice of colour
            self.part_id=i
            x, y, orientation = self.get_part_location(self.part_id)
            if x is None:
                return
            #print("[D]: Position: ", position, " orientation = ", orientation)
            self.move_arm(x, y, orientation, self.part_id)
            self.place_part(self.part_id)"""
        #Following 8 lines are only used until the move robot can handle fuse and pcb
        self.part_id = PartEnum.BACKCOVER.value
        x, y, orientation = self.get_part_location(self.part_id)
        if x is None:
            return
        # print("[D]: Position: ", position, " orientation = ", orientation)
        self.move_arm(x, y, orientation, self.part_id)
        self.place_part(self.part_id)
        x, y, orientation = self.get_part_location(self.colour_id) #3: black, 4: white, 5: blue
        if x is None:
            return
        self.move_arm(x, y, orientation, self.colour_id)
        self.place_part(self.colour_id)

    def place_part(self, part_id):
        if part_id == PartEnum.BACKCOVER.value:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        elif part_id == PartEnum.PCB.value:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        elif part_id == PartEnum.FUSE.value:
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        elif 2 < part_id < 6: #ANY colour front cover
            print("[I] Placing: ", self.utils.part_id_to_name(part_id))
        else:
            print("[WARNING] wrong part. ID recieved: ", part_id)

        #Following if-else statement is used for simple placing in a stack
        if part_id == PartEnum.BACKCOVER.value:
            self.move_robot.place(FIXTURE_X, FIXTURE_Y, part_id)
        else:
            self.move_robot.place(FIXTURE_X, FIXTURE_Y, part_id, 30)

    def move_arm(self, x, y, orientation, part_id):
        print("[I] Moving arm")
        self.move_robot.grip(x, y, orientation, part_id)
        self.in_zero_position = False

    def get_part_location(self, part_id):
        class_names = ClassConverter.convert_part_id(part_id)
        x, y, orientation = self.vision.detect_object(class_names)
        x, y, _ = self.aruco.calibrate(self.np_image, x, y)
        if x == -1 and y == -1:
            print("[W]: Could not find required part in image, please try again. Part: ", self.utils.part_id_to_name(part_id))
            return None, None, None
        else:
            return x, y, orientation

    def choose_action(self):
        print("Please write a command (write 'help' for a list of commands):")
        command = input()
        if command == "help":
            print(
                "Possible commands are: \nblack: assemble phone with black cover \nwhite: assemble phone with white cover \n"
                "blue: assemble phone with blue cover \nzero: put the robot in zero position \nquit: close the program")
        elif command == "black":
            self.colour_id = PartEnum.BLACKCOVER.value
            self.main_flow(controller.colour_id)
        elif command == "white":
            self.colour_id = PartEnum.WHITECOVER.value
            self.main_flow(controller.colour_id)
        elif command == "blue":
            self.colour_id = PartEnum.BLUECOVER.value
            self.main_flow(controller.colour_id)
        elif command == "zero":
            self.move_robot.move_out_of_view()
        elif command == "quit":
            exit(0)
        else:
            print("Invalid command, please try again")


controller = Controller()

while True:
    controller.choose_action()