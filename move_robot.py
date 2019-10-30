import socket
import time
import math
import urx


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
                    self.gripper.close()
                    exit(1)
            else:
                done = True

        self.suction_enable_pin = 6
        self.home_pose = [35, -300, 300, 0, 0, -0.8]
        self.move_out_of_view_pose = [-350, -35, 300, 0, 0, 0]
        self.default_orientation = [0, 0, 0]
        self.gripper_tcp = [0, 0, 0.1535, 2.9024, -1.2023, 0]
        self.fuse_tcp = [0.05455, -0.00109, 0.13215, -1.7600, -0.7291, 1.7601]
        self.suction_tcp = [-0.12, 0, 0.095, 0, 1.5707, 0]
        self.current_part_id = None
        self.grip_has_been_called_flag = False

        self.move_gripper(0)
        self.move_gripper(100)

    def __del__(self):
        self.stop_all()

    def stop_all(self):
        self.robot.stop()
        msg = "bye()\n"
        msg = msg.encode()
        self.gripper.send(msg)
        self.gripper.close()
        self.disable_suction()
        self.robot.close()
        print("[INFO] Safely stopped robot and gripper")

    def movel(self, pose, acc=1.0, vel=0.05, wait=True, relative=False):
        pose_local = pose.copy()
        pose_local[0] *= 0.001
        pose_local[1] *= 0.001
        pose_local[2] *= 0.001
        print(pose_local)
        self.robot.movel(pose_local, acc=acc, vel=vel, wait=wait, relative=relative)

    def move_to_home(self, orientation_offset=0.0, speed=1.0):
        home_pose_local = self.home_pose.copy()
        home_pose_local[5] += orientation_offset
        self.movel(home_pose_local, acc=1.0, vel=speed)

    def move_out_of_view(self, speed=1.0):
        self.move_to_home()
        self.robot.set_tcp(self.gripper_tcp)
        self.movel(self.move_out_of_view_pose, acc=1.0, vel=speed)

    def open_gripper(self):
        msg = "release(100)\n"
        msg = msg.encode()
        self.gripper.send(msg)
        time.sleep(1)

    def close_gripper(self):
        msg = "grip(20,0)\n"
        msg = msg.encode()
        self.gripper.send(msg)
        time.sleep(3)

    def move_gripper(self, position):
        msg = "move({})\n".format(position)
        msg = msg.encode()
        self.gripper.send(msg)
        time.sleep(1)

    def enable_suction(self):
        self.robot.set_digital_out(self.suction_enable_pin, True)

    def disable_suction(self):
        self.robot.set_digital_out(self.suction_enable_pin, False)

    def grip(self, x, y, orientation, part_id): # 0 = part horizontal, 1 = part vertical
        self.move_to_home()
        self.current_part_id = part_id
        self.grip_has_been_called_flag = True
        if part_id == 1: #PCB
            orientation_vector = [0, 0, -1.57]
            self.robot.set_tcp(self.suction_tcp)
            self.move_to_home()
            self.movel([x, y, 40] + orientation_vector, acc=1, vel=1)
            self.enable_suction()
            self.movel([x, y, 0] + orientation_vector, acc=0.1, vel=0.2)
            self.movel([x, y, 40] + orientation_vector, acc=0.1, vel=0.2)

        elif part_id == 2: #fuse
            self.robot.set_tcp(self.fuse_tcp)
            self.move_to_home()
            if orientation == 0: # part horizontal
                angle = -90 #DONE
                angle = math.radians(angle)
                angle -= 0
                orientation_vector = [0, 0, angle]
            else: # part vertical
                angle = 180 #DONE
                angle = math.radians(angle)
                angle -= 0
                orientation_vector = [0, 0, angle]
            self.movel([x, y, 20] + orientation_vector, acc=1, vel=1)
            self.close_gripper()
            self.movel([x, y, 2] + orientation_vector, acc=0.1, vel=0.2)
            self.movel([x, y, 20] + orientation_vector, acc=0.1, vel=0.2)

        else: #covers
            if orientation == 0:
                angle = 90
                angle = math.radians(angle)
                orientation_vector = [0, 0, angle]
            else:
                angle = 0
                angle = math.radians(angle)
                orientation_vector = [0, 0, angle]
            self.robot.set_tcp(self.gripper_tcp)
            self.move_to_home()
            self.movel([x, y, 20] + orientation_vector, acc=1, vel=1)
            self.open_gripper()
            self.movel([x, y, 0.5] + orientation_vector, acc=0.1, vel=0.4)
            self.close_gripper()
            self.movel([x, y, 20] + orientation_vector, acc=0.1, vel=0.4)

    def place(self, x, y, z_offset=0):
        if self.grip_has_been_called_flag:
            self.move_to_home()
            self.movel([x, y, 20 + z_offset] + self.default_orientation, acc=1, vel=1)
            self.movel([x, y, 0.5 + z_offset] + self.default_orientation, acc=0.1, vel=0.4)
            if self.current_part_id == 1: # PCB
                self.disable_suction()
            elif self.current_part_id == 2: # fuse
                self.open_gripper()
            else: # covers
                self.open_gripper()
            self.movel([x, y, 20] + self.default_orientation, acc=0.1, vel=0.4)
        else:
            print("[FATAL] place() was called before grip has been called! Exiting")
            self.stop_all()
        self.grip_has_been_called_flag = False



if __name__ == "__main__":
    robot = MoveRobot("192.168.1.148")
    time.sleep(1)
    print("init done")

    robot.grip(0, -500, 0, 1)
    robot.place(80, -300, 0)
    robot.move_to_home()

    robot.stop_all()

"""
    test_positions = [[-300, -280, 10], [-160, -180, 0], [30, -580, 0], [300, -350, 0], [50, -560, 0], [0, -320, 0], [130, -130, 0]]
    robot.robot.set_tcp(robot.gripper_tcp)
    robot.move_to_home()

    for pos in test_positions:
        robot.movel(pos + [0, 0, 0], vel=0.5)
        robot.move_to_home()

    robot.robot.set_tcp(robot.fuse_tcp)
    robot.move_to_home()
    for pos in test_positions:
        robot.movel(pos + [0, 0, -3.14], vel=0.5)
        robot.move_to_home()

    robot.robot.set_tcp(robot.suction_tcp)
    robot.move_to_home()
    for pos in test_positions:
        robot.movel(pos + [0, 0, -1.57], vel=0.5)
        robot.move_to_home()
"""


"""
fuses orientation, 90, 0

covers 180, 0, orientation

"""