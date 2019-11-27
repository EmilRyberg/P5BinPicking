from controller import Controller
from laser_scanner import LaserScanner
import threading

if __name__ == "__main__":
    controller = Controller()
    laser_scanner = LaserScanner()
    quit_program = False
    person_close = False

    person_close = threading.Thread(target=laser_scanner.check_distances())
    if person_close:
        print("Human entered danger zone, stopping system")
        exit(1)
    while not quit_program:
        quit_program = controller.choose_action()

