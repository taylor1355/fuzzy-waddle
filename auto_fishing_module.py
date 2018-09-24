from enum import Enum
import sys, os, time
import pyautogui
import cv2 as cv
import numpy as np
import random

from actions import Action
import direct_input
import input

from fishing_key_sequence import KeySequenceDetector

sys.path.append("ml")
from ml.model import Model

do_actions = True
show_image = True
output_chars = False

class AutoFishingModule():
    def __init__(self):
        self.isEnabled = True
        self.reelInFishAction = Action(0, self.reelInFish)
        self.castLineAction = Action(0, self.castLine)

        self.last_frame = None
        self.state = State.WAIT_SPACEBAR

        self.keySequenceDetector = KeySequenceDetector()
        self.spacebar_model = Model.load("ml/spacebar/spacebar_model.pkl")

        self.cast_reel_threshold = 217
        self.spacebar_height, self.spacebar_width = self.spacebar_model.box_size
        start_x, start_y = 575, 200
        box_width, box_height = self.spacebar_width, int(1.5 * self.spacebar_height)
        self.spacebar_search_box = (start_x, start_x + box_width, start_y, start_y + box_height)

    def getActions(self, frame):
        self.last_frame = frame
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        spacebar_prediction = self.predict_spacebar()
        spacebar_detected = spacebar_prediction is not None
        cast = spacebar_detected and spacebar_prediction[1] > self.cast_reel_threshold

        if spacebar_detected:
            print("detected at {}".format(spacebar_prediction))

        actions = []
        if self.state == State.WAIT_SPACEBAR:
            if cast:
                self.state = State.CAST
            elif spacebar_detected:
                self.state = State.REEL
        if self.state == State.CAST:
            actions = [self.castLineAction]
            self.state = self.state.next()
        elif self.state == State.WAIT_AFTER_CAST:
            if not spacebar_detected:
                self.state = self.state.next()
        elif self.state == State.REEL:
            actions = [self.reelInFishAction]
            self.state = self.state.next()

        if show_image:
            img = np.array(frame)

            font = cv.FONT_HERSHEY_SIMPLEX
            if spacebar_detected:
                cv.rectangle(img, (spacebar_prediction[0], spacebar_prediction[1]), (spacebar_prediction[0] + self.spacebar_width, spacebar_prediction[1] + self.spacebar_height), (0, 0, 255), 2)
                if cast:
                    text = "Cast Space Bar Detected"
                else:
                    text = "Reel Space Bar Detected"
                cv.putText(img, text, (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)
            else:
                cv.putText(img, "Idle Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)

            min_x, max_x, min_y, max_y = self.spacebar_search_box
            cv.rectangle(img, (min_x, min_y), (max_x, max_y), (255,0,0), 1)
            cv.imshow("output", img)
            cv.waitKey(1)

        if not do_actions:
            return []
        return actions

    def predict_spacebar(self):
        min_x, max_x, min_y, max_y = self.spacebar_search_box
        search_region = self.last_frame[min_y : max_y, min_x : max_x]
        class_detected, prediction = self.spacebar_model.predict(search_region)
        if class_detected == 1:
            return prediction + np.array([min_x, min_y])
        return None

    def reelInFish(self):
        direct_input.PressKey("SPACE")
        print("reeling in")
        direct_input.ReleaseKey("SPACE")
        time.sleep(1.7)
        direct_input.PressKey("SPACE")
        print("playing game")
        direct_input.ReleaseKey("SPACE")
        time.sleep(2.5)
        self.keySequenceDetector.processFrames(2, 2)
        keySequence = self.keySequenceDetector.getKeySequence()
        print("keys: " + str(keySequence))
        for key in keySequence:
            self.tapKey(key)
        time.sleep(3)
        self.tapKey(4)

    def castLine(self):
        direct_input.PressKey("SPACE")
        print("casting line")
        direct_input.ReleaseKey("SPACE")
        time.sleep(5)

    def sleep(self):
        sleep_time = 0.02 + np.clip(random.gauss(0.03, 0.01), 0, 0.06)
        time.sleep(sleep_time)

    def tapKey(self, key):
        key_string = ""
        if key == 0:
            key_string = "W"
        elif key == 1:
            key_string = "A"
        elif key == 2:
            key_string = "S"
        elif key == 3:
            key_string = "D"
        else:
            key_string = "R"
        direct_input.PressKey(key_string)
        self.sleep()
        direct_input.ReleaseKey(key_string)
        self.sleep()

class State(Enum):
    WAIT_SPACEBAR = 0
    CAST = 1
    WAIT_AFTER_CAST = 2
    REEL = 3

    def next(self):
        if self == State.WAIT_AFTER_CAST:
            next_state = State.WAIT_SPACEBAR
        else:
            next_state = State((self.value + 1) % len(State))
        print("Exited State: {}".format(self))
        print("Entered State: {}".format(next_state))
        return next_state
