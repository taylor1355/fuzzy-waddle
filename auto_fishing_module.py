from enum import Enum
import sys, os, time
import pyautogui
import cv2 as cv
import numpy as np

from actions import Action
import direct_input
import input

sys.path.append("ml")
from ml.model import Model

start_target_x = 575
start_target_y = 256
catch_target_x = 575
catch_target_y = 243
do_actions = True
show_image = False

class AutoFishingModule():
    def __init__(self):
        self.isEnabled = True
        self.reelInFishAction = Action(0, self.reelInFish)
        self.castLineAction = Action(0, self.castLine)

        self.last_frame = None
        self.state = State.CAST

        self.spacebar_model = Model.load("ml/spacebar/spacebar_model.pkl")
        self.spacebar_height, self.spacebar_width = self.spacebar_model.box_size

    def getActions(self, frame):
        self.last_frame = frame
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        cast_spacebar_region = self.region_of_interest(start_target_x, start_target_y, self.spacebar_width, self.spacebar_height)
        reel_spacebar_region = self.region_of_interest(catch_target_x, catch_target_y, self.spacebar_width, self.spacebar_height)

        spacebar_prediction = self.predict_spacebar()
        spacebar_detected = spacebar_prediction is not None

        actions = []
        if self.state == State.CAST:
            actions = [self.castLineAction]
            self.state = self.state.next()
        elif self.state == State.WAIT_AFTER_CAST:
            if not spacebar_detected:
                self.state = self.state.next()
        elif self.state == State.WAIT_REEL:
            if spacebar_detected:
                self.state = self.state.next()
        elif self.state == State.REEL:
            actions = [self.reelInFishAction]
            self.state = self.state.next()
        elif self.state == State.WAIT_KEYS or self.state == State.KEYS:
            self.state = self.state.next()
        elif self.state == State.WAIT_CAST:
            if spacebar_detected:
                self.state = self.state.next()

        if show_image:
            img = np.array(frame)

            font = cv.FONT_HERSHEY_SIMPLEX
            if (spacebar_detected):
                cv.putText(img, "Space Bar Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)
                cv.rectangle(img, (spacebar_prediction[0], spacebar_prediction[1]), (spacebar_prediction[0] + self.spacebar_width, spacebar_prediction[1] + self.spacebar_height), (0, 0, 255), 2)
            else:
                cv.putText(img, "Idle Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)

            cv.rectangle(img, (start_target_x, 200), (start_target_x + self.spacebar_width, 320), (255,0,0), 1)
            cv.imshow("output", img)
            cv.waitKey(0)

        if not do_actions:
            return []
        return actions

    def predict_spacebar(self):
        search_region = self.region_of_interest(start_target_x, 200, self.spacebar_width, 120)
        spacebar_detected, prediction = self.spacebar_model.predict(search_region)
        if spacebar_detected:
            return prediction + np.array([start_target_x, 200])
        return None

    def region_of_interest(self, min_x, min_y, width, height):
        return self.last_frame[min_y : min_y+height, min_x : min_x+width]

    def reelInFish(self):
        direct_input.PressKey("SPACE")
        print("reeling in")
        direct_input.ReleaseKey("SPACE")
        time.sleep(1.7)
        direct_input.PressKey("SPACE")
        print("playing game")
        direct_input.ReleaseKey("SPACE")
        time.sleep(10)

    def castLine(self):
        direct_input.PressKey("SPACE")
        print("casting line")
        direct_input.ReleaseKey("SPACE")
        time.sleep(5)

class State(Enum):
    CAST = 0
    WAIT_AFTER_CAST = 1
    WAIT_REEL = 2
    REEL = 3
    WAIT_KEYS = 4
    KEYS = 5
    WAIT_CAST = 6

    def next(self):
        next_state = State((self.value + 1) % len(State))
        print("Exited State: {}".format(self))
        print("Entered State: {}".format(next_state))
        return next_state
