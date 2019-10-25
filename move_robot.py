import sys
import urx
import time
from urx import RobotException
import logging
import socket
from utils import Utils
import math


class MoveRobot:
    def __init__(self, ip):
        done = False
        counter = 0
        gripper_ip = "192.168.1.118"
        gripper_port = 1000
        while not done:
            try:
                self.robot = urx.Robot(ip)
            except Exception as e:
                if e.args[0] == "timed out":
                    print("[ERROR] Connection to the robot timed out. Check IP address")
                    exit(1)
                elif e.args[0] == "Did not receive a valid data packet from robot in 0.5" and counter < 10:
                    time.sleep(0.5)
                    print("Robot didn't respond, retrying, try %s/10" % counter)
                    counter += 1
                else:
                    print(e)
                    exit(1)
            else:
                done = True
        done = False
        counter = 0
        while not done:
            try:
                self.gripper = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.gripper.connect((gripper_ip, gripper_port))
            except Exception as e:
                counter += 1
                print(e)
                print("[WARNING] Couldn't connect to gripper, try %s" % counter)
                time.sleep(0.2)
                if counter > 10:
                    print("[FATAL] Couldn't connect to gripper, exiting.")
                    exit(1)
            else:
                done = True

        self.gripper_open_pin = 4
        self.gripper_close_pin = 5
        self.suction_enable_pin = 6
        self.home_pose = [35, -350, 300, 3.14, 0, 0]
        self.move_out_of_view_pose = [-350, -35, 300, 3.14, 0, 0]
        self.default_orientation = [3.14, 0, 0]

    def __del__(self):
        msg = "bye()\n"
        msg = msg.encode()
        self.gripper.send(msg)
        print("sent disconnect to gripper")

    def movel(self, pose, acc=1.0, vel=0.05, wait=True, relative=False):
        pose_local = pose[:]
        pose_local[0] *= 0.001
        pose_local[1] *= 0.001
        pose_local[2] *= 0.001
        self.robot.movel(pose_local, acc=acc, vel=vel, wait=wait, relative=relative)

    def move_to_home(self, speed=1.0):
        self.movel(self.home_pose, acc=1.0, vel=speed)

    def move_out_of_view(self, speed=1.0):
        self.movel(self.move_out_of_view_pose, acc=1.0, vel=speed)

    def open_gripper(self):
        msg = "release(30)\n"
        msg = msg.encode()
        self.gripper.send(msg)
        time.sleep(1)

    def close_gripper(self):
        msg = "grip(20,0)\n"
        msg = msg.encode()
        self.gripper.send(msg)
        time.sleep(3)

    def enable_suction(self):
        self.robot.set_digital_out(self.suction_enable_pin, True)

    def disable_suction(self):
        self.robot.set_digital_out(self.suction_enable_pin, False)

    def grip(self, x, y, orientation, part_id):
        self.move_to_home()
        if part_id == 1 or part_id == 1: #PCB
            pass
        elif part_id == 2: #fuse
            pass
        else: #covers
            orientation_vector = None
            if orientation == 0: #horizontal
                #orientation_vector = Utils.rpy_to_rot_vect(180, 0, 45)
                orientation_vector = [2.9, -1.2, 0]
            else:
                #orientation_vector = Utils.rpy_to_rot_vect(180, 0, 45 + 90)
                orientation_vector = [1.2, -2.9, 0]
            self.movel([x, y, 20] + orientation_vector, acc=1, vel=1)
            self.open_gripper()
            self.movel([x, y, 0.5] + orientation_vector, acc=0.1, vel=0.02)
            self.close_gripper()
            self.movel([x, y, 20] + orientation_vector, acc=0.1, vel=0.02)

    def place(self, x, y, type):
        self.move_to_home()
        self.movel([x, y, 20] + self.default_orientation, acc=1, vel=1)
        self.movel([x, y, 0.5] + self.default_orientation, acc=0.1, vel=0.02)
        self.open_gripper()
        self.movel([x, y, 20] + self.default_orientation, acc=0.1, vel=0.02)


if __name__ == "__main__":
    a = Utils.rpy_to_rot_vect(-180, 0, 45)

    robot = MoveRobot("192.168.1.148")
    time.sleep(1)

    robot.close_gripper()
    robot.open_gripper()

    robot.grip(0, -400, 0, 0)
    robot.place(0, -200, 0)


    time.sleep(3)
    robot.__del__()
    exit()

"""
fuses orientation, 90, 0

covers 180, 0, orientation

"""