from utils import part_id_to_name
from move_robot import MoveRobot
from vision import Vision
from enums import PartEnum
from class_converter import convert_from_part_id
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
        parts_to_flip = self.vision.find_flipped_parts()

        z_offset = 0
        should_flip_part = self.parts_to_flip_contains(parts_to_flip, PartEnum.BACKCOVER.value)
        self.pick_and_place_part(PartEnum.BACKCOVER.value, z_offset, should_flip_part)

        z_offset = 20
        should_flip_part = self.parts_to_flip_contains(parts_to_flip, PartEnum.PCB.value)
        self.pick_and_place_part(PartEnum.PCB.value, z_offset, should_flip_part)

        z_offset = 30
        self.pick_and_place_part(PartEnum.FUSE.value, z_offset, fuse_id=0)
        self.pick_and_place_part(PartEnum.FUSE.value, z_offset, fuse_id=1)

        z_offset = 30
        should_flip_part = self.parts_to_flip_contains(parts_to_flip, colour_part_id)
        self.pick_and_place_part(colour_part_id, z_offset, should_flip_part)

        self.move_robot.move_out_of_view()

    def pick_and_place_part(self, part_id, z_offset, should_be_flipped=False, fuse_id=0):
        x, y, orientation = self.get_part_location(part_id)
        while x is None:
            print("[W]: Could not find required part in image, please move the part and try again. Part: ",
                  part_id_to_name(part_id))
            input("Press Enter to continue...")
            self.get_image()
            x, y, orientation = self.get_part_location(part_id)
        # print("[D]: Position: ", position, " orientation = ", orientation)
        self.move_and_grip(x, y, orientation, part_id)

        # self.move_robot.align(part_id, should_be_flipped)

        if not part_id == PartEnum.FUSE.value:
            if not part_id == PartEnum.PCB.value:
                self.move_robot.move_to_camera(is_pcb=False)
            else:
                self.move_robot.move_to_camera(is_pcb=True)

        np_image = self.vision.capture_image()
        is_facing_right = self.vision.is_facing_right(np_image)

        if is_facing_right:
            self.move_robot.place(FIXTURE_X, FIXTURE_Y, z_offset, reorient=False)
        else:
            self.move_robot.place(FIXTURE_X, FIXTURE_Y, z_offset, reorient=False)

    def move_and_grip(self, x, y, orientation, part_id):
        print("[I] Moving arm")
        self.move_robot.grip(x, y, orientation, part_id)

    def get_part_location(self, part_id):
        class_names = convert_from_part_id(part_id)
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

    def parts_to_flip_contains(self, parts_to_flip, part_id):
        filtered_array = [part for part in parts_to_flip if part[0] == part_id]
        return True if len(filtered_array) > 0 else False

    def get_image(self):
        self.move_robot.move_out_of_view()
        self.np_image = self.vision.capture_image()

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
