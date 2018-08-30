import os, sys, time
import pyautogui
import cv2 as cv
import numpy as np

from game_window import GameWindow
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

        self.thread = StreamThread()

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

class StreamThread(QThread):
    def __init__(self):
        super(StreamThread, self).__init__()

    def __del__(self):
        self.wait()

    def getState(self): # idle=0, start=1, catch=2
        self.window.move_to_foreground()

        self.stream_img = self.window.grab_frame()
        stream_gray = cv.cvtColor(self.stream_img, cv.COLOR_BGR2GRAY)

        method = cv.TM_SQDIFF
        result = cv.matchTemplate(self.comp_img, stream_gray, method)
        mn, _, mnLoc, _ = cv.minMaxLoc(result)
        MPx, MPy = mnLoc

        status = 0

        if (MPx > start_target_x - target_thresh and MPx < start_target_x + target_thresh and MPy > start_target_y - target_thresh and MPy < start_target_y + target_thresh):
            return 1
        elif (MPx > catch_target_x - target_thresh and MPx < catch_target_x + target_thresh and MPy > catch_target_y - target_thresh and MPy < catch_target_y + target_thresh):
            return 2
        else:
            return 0

    def actions(self, action):
        if (action == 1):
            direct_input.PressKey("SPACE")
            print("casting line")
            direct_input.ReleaseKey("SPACE")
            time.sleep(5)
        elif (action == 2):
            direct_input.PressKey("SPACE")
            print("reeling in")
            direct_input.ReleaseKey("SPACE")
            time.sleep(1.7)
            direct_input.PressKey("SPACE")
            print("playing game")
            direct_input.ReleaseKey("SPACE")
            time.sleep(10)



    def run(self):
        self.window = GameWindow("BLACK DESERT")
        self.window.move_to_foreground()

        point = self.window.rect.center()
        pyautogui.moveTo(point[0], point[1], duration=2)

        comp_path = "ref_images/fishing_space_bar.jpg"
        self.comp_img = cv.imread(comp_path, 0)

        while 1:
            state = self.getState()

            if (actions):
                if (state == 1):
                    # space bar
                    self.actions(1)
                elif (state == 2):
                    self.actions(2)

            else:
                self.stream_img = self.window.grab_frame()
                stream_gray = cv.cvtColor(self.stream_img, cv.COLOR_BGR2GRAY)

                method = cv.TM_SQDIFF
                result = cv.matchTemplate(self.comp_img, stream_gray, method)
                mn, _, mnLoc, _ = cv.minMaxLoc(result)
                MPx, MPy = mnLoc
                trows,tcols = self.comp_img.shape[:2]
                font = cv.FONT_HERSHEY_SIMPLEX
                if (state == 0):
                    # idle
                    cv.putText(self.stream_img, "Idle Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)
                elif (state == 1):
                    # space bar
                    cv.putText(self.stream_img, "Space Bar Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)

                print(str(MPx) + " " + str(MPy))
                cv.rectangle(self.stream_img, (MPx, MPy), (MPx + tcols, MPy + trows), (0, 0, 255), 2)
                cv.imshow("output", self.stream_img)
                cv.waitKey(0)
                cv.destroyAllWindows()

            print("sleeping...")
            time.sleep(1)

        print("leaving")