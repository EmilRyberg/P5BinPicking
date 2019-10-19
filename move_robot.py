import sys
import urx
import time
from urx import RobotException
import logging


class MoveRobot:
    def __init__(self, ip):
        done = False
        counter = 0
        while not done:
            try:
                self.robot = urx.Robot(ip)
            except Exception as e:
                if e.args[0] == "timed out":
                    print("[ERROR] Connection to the robot timed out. Check IP address")
                    exit(1)
                elif e.args[0] == "Did not receive a valid data packet from robot in 0.5" and counter < 2:
                    time.sleep(0.5)
                    print("Robot didn't respond, retrying")
                    counter += 1
                else:
                    print(e)
                    exit(1)
            else:
                done = True
        self.gripper_open_pin = 0  # TODO update pins
        self.gripper_close_pin = 0
        self.suction_enable_pin = 0
        self.home_pose = [0, 0, 200, 0, 0, 0]  # TODO update
        self.move_out_of_view_pose = [0, 0, 200, 0, 0, 0]
        self.default_orientation = [0, 0, 0] # TODO update

    def movel(self, pose, acc=1.0, vel=0.05, wait=True, relative=False, threshold=0.001):
        counter = 0
        done = False
        pose[0] *= 0.001
        pose[1] *= 0.001
        pose[2] *= 0.001
        while not done:
            try:
                self.robot.movel(pose, acc=acc, vel=vel, wait=wait, relative=relative, threshold=threshold)
            except RobotException as e:
                print(e)
                time.sleep(0.2)
                counter += 1
                robot_is_already_in_pose = True
                current_pose = self.robot.getl()
                for i in range(6):
                    if abs(current_pose[i] - pose[i]) > 0.001:
                        robot_is_already_in_pose = False
                if robot_is_already_in_pose:
                    print("[INFO] Robot is already in pose")
                    done = True
                elif not self.robot.is_program_running():
                    print("[WARNING] Robot couldn't start, try %s", counter)
                    print(e)
                    time.sleep(0.2)
                    if counter > 10:
                        raise Exception("Robot couldn't start after %s tries", counter)
                else:
                    done = True
            except (KeyboardInterrupt, SystemExit):
                print("[FATAL] received program stop interrupt")
                self.robot.stopj()
                print("[INFO] Stopping robot")
                raise
            else:
                done = True

    def move_to_home(self, speed=1):
        self.movel(self.home_pose, acc=1, vel=speed)

    def move_out_of_view(self, speed=1):
        self.movel(self.move_out_of_view_pose, acc=1, vel=speed)

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

    def grip(self, x, y, type):
        # TODO figure out how to handle part types' tcp offsets
        self.move_to_home()
        self.movel([x, y, 20]+self.default_orientation, acc=1, vel=1)
        self.open_gripper()
        self.movel([x, y, 0.5]+self.default_orientation, acc=0.1, vel=0.02)
        self.close_gripper()
        self.movel([x, y, 20]+self.default_orientation, acc=0.1, vel=0.02)

    def place(self, x, y, type):
        self.move_to_home()
        self.movel([x, y, 20]+self.default_orientation, acc=1, vel=1)
        self.movel([x, y, 0.5]+self.default_orientation, acc=0.1, vel=0.02)
        self.open_gripper()
        self.movel([x, y, 20]+self.default_orientation, acc=0.1, vel=0.02)

if __name__ == "__main__":
    robot = MoveRobot("192.168.137.195")
    time.sleep(1)
    robot.robot.getl()
    time.sleep(1)
    robot.movel([-120, -125, 500, 1.5, -2.7, 0], wait=True)
    print("111111111111")
    print(robot.robot.getl())
    for i in range(10):
        print(robot.robot.is_running())
        time.sleep(0.5)
    exit(0)
    time.sleep(1)
    robot.movel([-120,-125, 300, 1.5, -2.7, 0], wait=True)
    print("DONE")