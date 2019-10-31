from utils import part_id_to_name
from move_robot import MoveRobot
from vision import Vision
from enums import PartEnum
from class_converter import convert_part_id
from aruco import Calibration
from PIL import Image as pimg
import numpy as np

NUMBER_OF_PARTS = 4
FIXTURE_X = 255
FIXTURE_Y = -320
UR_IP = "192.168.1.148"


class Controller:
    def __init__(self):
        self.np_image = None
        self.move_robot = MoveRobot(UR_IP)
        self.vision = Vision()
        self.aruco = Calibration()

        print("[I] Controller running")

    def main_flow(self, colour_id):
        self.get_image()
        self.flip_parts()
        z_offset = 0
        for i in range(NUMBER_OF_PARTS - 1): #leaving front cover out for later choice of colour
            part_id = i
            x, y, orientation = self.get_part_location(part_id)
            while x is None:
                print("[W]: Could not find required part in image, please move the part and try again. Part: ", part_id_to_name(part_id))
                input("Press Enter to continue...")
                self.get_image()
                x, y, orientation = self.get_part_location(part_id)
            #print("[D]: Position: ", position, " orientation = ", orientation)
            self.move_arm(x, y, orientation, part_id)
            self.place_part(part_id, z_offset)
            z_offset += 25
        x, y, orientation = self.get_part_location(colour_id) #3: black, 4: white, 5: blue
        while x is None:
            print("[W]: Could not find required part in image, please move the part and try again. Part: ", part_id_to_name(colour_id))
            input("Press Enter to continue...")
            self.get_image()
            x, y, orientation = self.get_part_location(colour_id)
        self.move_arm(x, y, orientation, colour_id)
        self.place_part(colour_id, z_offset)

    def place_part(self, part_id, z_offset):
        if part_id == PartEnum.BACKCOVER.value:
            print("[I] Placing: ", part_id_to_name(part_id))
        elif part_id == PartEnum.PCB.value:
            print("[I] Placing: ", part_id_to_name(part_id))
        elif part_id == PartEnum.FUSE.value:
            print("[I] Placing: ", part_id_to_name(part_id))
        elif 2 < part_id < 6: #ANY colour front cover
            print("[I] Placing: ", part_id_to_name(part_id))
        else:
            print("[WARNING] wrong part. ID recieved: ", part_id)

        #Following if-else statement is used for simple placing in a stack
        self.move_robot.place(FIXTURE_X, FIXTURE_Y, z_offset)

    def move_arm(self, x, y, orientation, part_id):
        print("[I] Moving arm")
        self.move_robot.grip(x, y, orientation, part_id)

    def get_part_location(self, part_id):
        class_names = convert_part_id(part_id)
        x, y, orientation = self.vision.detect_object(class_names)
        if x == -1 and y == -1:
            return None, None, None
        x, y, _ = self.aruco.calibrate(self.np_image, x, y)
        if part_id == PartEnum.FUSE.value:
            fuse_in_restricted_area = self.fuse_area_check(y)
            while fuse_in_restricted_area:
                print("[W]: Fuse found in restricted area, y =", y, " please move the fuse closer to the robot")
                input("Press Enter to continue...")
                self.get_image()
                x, y, orientation = self.vision.detect_object(class_names)
                x, y, _ = self.aruco.calibrate(self.np_image, x, y)
                fuse_in_restricted_area = self.fuse_area_check(y)
            return x, y, orientation
        else:
            return x, y, orientation

    def fuse_area_check(self, fuse_y):
        if fuse_y < -500:
            return True
        else:
            return False

    def get_image(self):
        self.move_robot.move_out_of_view()
        self.np_image = self.vision.capture_image()

    def flip_parts(self):
        parts_to_flip = self.vision.find_flipped_parts()
        for i in range(len(parts_to_flip)):
            part = parts_to_flip[i]
            gripper = part[0]
            x = part[1]
            y = part[2]
            orientation = part[3]
            print("[D]: Trying to flip object similar to: ", part_id_to_name(gripper), " with coordinates, X: ", x, " and y: ", y)

    def choose_action(self):
        print("Please write a command (write 'help' for a list of commands):")
        command = input()
        if command == "help":
            print(
                "Possible commands are: \nblack: assemble phone with black cover \nwhite: assemble phone with white cover \n"
                + "blue: assemble phone with blue cover \nzero: put the robot in zero position \nquit: close the program")
        elif command == "black":
            self.main_flow(PartEnum.BLACKCOVER.value)
        elif command == "white":
            self.main_flow(PartEnum.WHITECOVER.value)
        elif command == "blue":
            self.main_flow(PartEnum.BLUECOVER.value)
        elif command == "zero":
            self.move_robot.move_out_of_view()
        elif command == "quit":
            return True
        else:
            print("Invalid command, please try again")

        return False
