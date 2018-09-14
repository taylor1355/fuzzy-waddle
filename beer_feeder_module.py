from enum import Enum
import sys, os, time
import pyautogui
import cv2 as cv
import numpy as np

from actions import Action
import direct_input
import input

from stream_test_tab import CharacterDetectionThread

sys.path.append("ml")
from ml.model import Model

inventory_x = 470
inventory_y = 60
inventory_width = 800
inventory_height = 470
zero_spot_open = False
#do_actions = False
#show_image = True
#output_chars = False

class BeerFeederModule():
    def __init__(self):
        self.isEnabled = True
        self.openInven = Action(0, self.openInventory)
        self.feedBeer = Action(0, self.feedBeerToWorkers)

        self.last_frame = None
        self.state = State.BASE


    def getActions(self, frame):
        self.last_frame = frame
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        inventory = self.region(inventory_x, inventory_y, self.inventory_width, self.inventory_height)


        #implementation of actions needs to be added debugging is here now
        if self.state == State.BASE:
            if (zero_spot_open):
                feedBeerToWorkers()
                self.state = self.state.next()
                self.state = self.state.next()
            else:
                openInventory()
                self.state = self.state.next()
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#edit what image we use
        if self.state == State.INVENTORY:
            search_image('green_beer.jpg')
            self.state = self.state.next()
        if self.state == State.FEEDING:
            search_image('recover.jpg')
            search_image('confirm.jpg')
            search_image('repeat.jpg')
            self.state = self.state.next()
        if self.state == State.WAIT:
            time.sleep(600)
            self.state = self.state.next()


#////////////////////////////////////////////////////////////////////////////////////////
#add in am image display

    def search_image(image_name):
        template = cv.imread("ref_images\\" + image_name,0)
        res = cv.matchTemplate(inventory,template,cv.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        moveMouse(max_loc[0],max_loc[1])

    def region(self, x, y, width, height):
        return self.last_frame[y : y+height, x : x+width]

    def feedBeerToWorkers(self):
        direct_input.PressKey("0")
        print("opening workers")
        direct_input.ReleaseKey("0")
        time.sleep(1)
    def moveMouse(self,x,y):
        #move to restart all button(mouse movement)
    def openIventory(self):
        direct_input.PressKey("I")
        print("opening inventory")
        direct_input.ReleaseKey("I")
        time.sleep(1)

class State(Enum):
    BASE = 0
    INVENTORY = 1
    FEEDING = 2
    WAIT = 3


    def next(self):
        next_state = State((self.value + 1) % len(State))
        print("Exited State: {}".format(self))
        print("Entered State: {}".format(next_state))
        return next_state
