import os, sys, time
import pyautogui
import cv2 as cv
import numpy as np

from game_window import GameWindow
from actions import Action
import direct_input
import input

import utils

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class AutoFishingTab(QWidget):
    def __init__(self):
        super(AutoFishingTab, self).__init__()
        startWorkerButton = utils.createButton("Start Worker", self, 0, 0)
        startWorkerButton.released.connect(self._start_worker_button_handler)
        stopWorkerButton = utils.createButton("Stop Worker", self, 0, 1)
        stopWorkerButton.released.connect(self._stop_worker_button_handler)

    def _start_worker_button_handler(self):
        print("starting worker")
        self.thread.start()

    def _stop_worker_button_handler(self):
        print("stopping worker")
        self.thread.terminate()


start_target_x = 574
start_target_y = 222
catch_target_x = 574
catch_target_y = 205
target_thresh = 5
actions = True

class AutoFishingModule():
    def __init__(self):
        self.isEnabled = True
        self.reelInFishAction = Action(0, self.reelInFish)
        self.castLineAction = Action(0, self.castLine)
        comp_path = "ref_images/fishing_space_bar.jpg"
        self.comp_img = cv.imread(comp_path, 0)

    def getActions(self, frame):
        self.lastFrame = frame

        stream_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        method = cv.TM_SQDIFF
        result = cv.matchTemplate(self.comp_img, stream_gray, method)
        mn, _, mnLoc, _ = cv.minMaxLoc(result)
        MPx, MPy = mnLoc

        state = 0
        if (MPx > start_target_x - target_thresh and MPx < start_target_x + target_thresh and MPy > start_target_y - target_thresh and MPy < start_target_y + target_thresh):
            state = 1
        elif (MPx > catch_target_x - target_thresh and MPx < catch_target_x + target_thresh and MPy > catch_target_y - target_thresh and MPy < catch_target_y + target_thresh):
            state = 2

        show_image = False
        if show_image:
            stream_gray = cv.cvtColor(window, cv.COLOR_BGR2GRAY)

            method = cv.TM_SQDIFF
            result = cv.matchTemplate(self.comp_img, stream_gray, method)
            mn, _, mnLoc, _ = cv.minMaxLoc(result)
            MPx, MPy = mnLoc
            trows,tcols = self.comp_img.shape[:2]
            font = cv.FONT_HERSHEY_SIMPLEX
            if (state == 0):
                cv.putText(self.stream_img, "Idle Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)
            elif (state == 1):
                cv.putText(self.stream_img, "Space Bar Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)

            print(str(MPx) + " " + str(MPy))
            cv.rectangle(self.stream_img, (MPx, MPy), (MPx + tcols, MPy + trows), (0, 0, 255), 2)
            cv.imshow("output", self.stream_img)
            cv.waitKey(0)
            cv.destroyAllWindows()

        if state == 1:
            return [self.castLineAction]
        elif state == 2:
            return [self.reelInFishAction]
        else:
            return []

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
