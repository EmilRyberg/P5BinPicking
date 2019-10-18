import sys
import urx
import time
from urx import RobotException


class MoveRobot:
    def __init__(self, ip):
        self.robot = urx.Robot(ip)
        self.gripper_open_pin = 0  # TODO update pins
        self.gripper_close_pin = 0
        self.suction_enable_pin = 0
        self.home_pose = [0, 0, 200, 0, 0, 0]  # TODO update
        self.zero_pose = [0, 0, 0, 0, 0, 0] # TODO update
        self.default_orientation = [0, 0, 0] # TODO update

    def movel(self, pose, acc=1.0, vel=0.05, wait=True, relative=False, threshold=None):
        counter = 0
        done = False
        while not done:
            try:
                self.robot.movel(pose, acc=acc, vel=vel, wait=wait, relative=relative, threshold=threshold)
            except RobotException as e:
                counter += 1
                print("[WARNING] Robot couldn't start, try %s", counter)
                print(e)
                time.sleep(0.2)
                if counter > 10:
                    raise Exception("Robot couldn't start after %s tries", counter)
            except:
                print("[FATAL] Something went wrong")
                self.robot.stopj()
                print("[INFO] Stopping robot")
                raise
            else:
                done = True

    def move_to_home(self, speed=1):
        self.movel(self.home_pose, acc=1, vel=speed)

    def move_to_zero(self, speed=1):
        self.movel(self.zero_pose, acc=1, vel=speed)

    def open_gripper(self):
        self.robot.set_digital_out(self.gripper_open_pin, True)
        self.robot.set_digital_out(self.gripper_close_pin, False)

    def close_gripper(self):
        self.robot.set_digital_out(self.gripper_open_pin, False)
        self.robot.set_digital_out(self.gripper_close_pin, True)

    def enable_suction(self):
        self.robot.set_digital_out(self.suction_enable_pin, True)

    def disable_suction(self):
        self.robot.set_digital_out(self.suction_enable_pin, False)

    def grip(self, x, y, orientation, part_id):
        # TODO figure out how to handle part types' tcp offsets
        self.move_to_home()
        self.movel([x, y, 20]+orientation, acc=1, vel=1)
        self.open_gripper()
        self.movel([x, y, 0.5]+orientation, acc=0.1, vel=0.02)
        self.close_gripper()
        self.movel([x, y, 20]+orientation, acc=0.1, vel=0.02)

    def place(self, x, y, type):
        self.move_to_home()
        self.movel([x, y, 20]+self.default_orientation, acc=1, vel=1)
        self.movel([x, y, 0.5]+self.default_orientation, acc=0.1, vel=0.02)
        self.open_gripper()
        self.movel([x, y, 20]+self.default_orientation, acc=0.1, vel=0.02)
