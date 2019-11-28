from pyurg import pyurg
import threading


STOP_THRESHOLD_LOW = 100
STOP_THRESHOLD_HIGH = 500
SLOW_THRESHOLD_LOW = 500
SLOW_THRESHOLD_HIGH = 1000


class Safety:
    def __init__(self):
        self.ignore_indexes = []
        self.person_close_counter = 0
        self.person_close = False
        self.person_approaching_counter = 0
        self.person_approaching = False
        self.led_thread_running = False
        self.scanner = pyurg.UrgDevice()
        if not self.scanner.connect():
            print('Could not connect to laser scanner.')
            exit(0)

        #Getting reference values to ignore
        data, timestamp = self.scanner.capture()
        for i in range(len(data)):
            if i == len(data) - 3:
                break
            elif STOP_THRESHOLD_LOW < data[i] < SLOW_THRESHOLD_HIGH and STOP_THRESHOLD_LOW < data[i + 1] < SLOW_THRESHOLD_HIGH and STOP_THRESHOLD_LOW < data[i + 2] < SLOW_THRESHOLD_HIGH:
                self.ignore_indexes.append(i)

    def check_distances(self, controller, x):
        led_flash_thread = threading.Thread(target=controller.move_robot.flash_led, args=(), daemon=True)
        while True:
            data, timestamp = self.scanner.capture()
            if timestamp == -1:
                print('Could not get laser scanner data')
                exit(0)
            else:
                for i in range(len(data)):
                    if i == len(data)-3:
                        break
                    elif i in self.ignore_indexes or i+1 in self.ignore_indexes or i-1 in self.ignore_indexes:
                        continue
                    elif STOP_THRESHOLD_LOW < data[i] < STOP_THRESHOLD_HIGH and STOP_THRESHOLD_LOW < data[i+1] < STOP_THRESHOLD_HIGH and STOP_THRESHOLD_LOW < data[i+2] < STOP_THRESHOLD_HIGH:
                        self.person_close_counter = self.person_close_counter+1

                    if i == len(data)-3:
                        break
                    elif i in self.ignore_indexes or i+1 in self.ignore_indexes or i-1 in self.ignore_indexes:
                        continue
                    elif SLOW_THRESHOLD_LOW < data[i] < SLOW_THRESHOLD_HIGH and SLOW_THRESHOLD_LOW < data[i+1] < SLOW_THRESHOLD_HIGH and SLOW_THRESHOLD_LOW < data[i+2] < SLOW_THRESHOLD_HIGH:
                        self.person_approaching_counter = self.person_approaching_counter+1

                if self.person_close_counter > 2: #To avoid environmental noise from stopping the robot
                    self.person_close = True
                    print("Warning: person close, stopping robot")
                    controller.move_robot.set_speed(0.5)
                    if self.led_thread_running:
                        led_flash_thread.join()
                        self.led_thread_running = False
                    controller.move_robot.turn_on_led()
                    self.person_close_counter = 0
                elif self.person_approaching_counter > 2:  # To avoid environmental noise from stopping the robot
                    self.person_approaching = True
                    print("Warning: person close, stopping robot")
                    controller.move_robot.set_speed(50)
                    led_flash_thread.start()
                    self.person_approaching_counter = 0
                elif self.person_close_counter < 2 and self.person_approaching_counter < 2:
                    self.person_close = False
                    self.person_approaching = False
                    if self.led_thread_running:
                        led_flash_thread.join()
                        self.led_thread_running = False
                    controller.move_robot.turn_off_led()
                    controller.move_robot.set_speed(100)



if __name__ == "__main__":
    safety = Safety()
    while True:
        safety.check_distances()