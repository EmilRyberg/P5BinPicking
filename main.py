import sys
import time

NUMBER_OF_PARTS = 4

class Controller(object):
    def __init__(self):
        self.in_zero_position = False
        self.colour_chosen = False
        print("Controller running")

    def main_flow(self):
        if (!self.in_zero_position):
            self.move_arm(zero_position, zero_orientation)
            self.in_zero_position = True
        for i in range(0, NUMBER_OF_PARTS-1): #leaving front cover out for later choice of colour
            position, orientation = self.get_object_location(i)
            self.move_arm(position, orientation)
            self.pick_up(i)
            self.place_object(i)
        while (self.colour_chosen == False):
            print("Choose colour of front cover: /n w = white /n ba = black /n bu = blue")
            cover_colour = input()
            if (cover_colour == "w"):
                object = 3
                position, orientation = self.get_object_location(object) #3 = white cover
                self.move_arm(position, orientation)
                self.pick_up(object)
                self.place_object(object)
                self.colour_chosen = True
            elif (cover_colour == "ba"):
                object = 4
                position, orientation = self.get_object_location(object) #4 = black cover
                self.move_arm(position, orientation)
                self.pick_up(object)
                self.place_object(object)
                self.colour_chosen = True
            elif (cover_colour == "bu"):
                object = 5
                position, orientation = self.get_object_location(object) #5 = blue cover
                self.move_arm(position, orientation)
                self.pick_up(object)
                self.place_object(object)
                self.colour_chosen = True
            else:
                print("Wrong colour chosen, please try again")

    def pick_up(self, object):
        if (object == 0):
            tool = "big gripper"
        elif (object == 1):
            tool = "suction"
        elif (object == 2):
            tool = "small gripper"
        else:
            print("[WARNING] wrong object")
            return

    def place_object(self, object):


    def move_arm(self, position, orientation):

        self.in_zero_position = False

    def get_object_location(self, object):
        location = (10.5, 20.1)
        orientation = 1
        return location


