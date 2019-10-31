from controller import Controller

if __name__ == "__main__":
    controller = Controller()
    quit_program = False
    while not quit_program:
        quit_program = controller.choose_action()
