from controller import Controller
from laser_scanner import LaserScanner
import threading

if __name__ == "__main__":
    controller = Controller()
    laser_scanner = LaserScanner()
    quit_program = False
    person_close = False

    laser_thread = threading.Thread(target=laser_scanner.check_distances, args=(controller, 0), daemon=True)
    laser_thread.start()

    while not quit_program:
        quit_program = controller.choose_action()

