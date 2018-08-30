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
        self.thread.start()

    def _stop_worker_button_handler(self):
        self.thread.terminate()


target_x = 574
target_y = 222
target_thresh = 3
actions = True

class StreamThread(QThread):
    def __init__(self):
        super(StreamThread, self).__init__()

    def __del__(self):
        self.wait()



    def actions(self, action):
        point = window.rect.center()
        pyautogui.moveTo(point[0], point[1], duration=2)
        sleep(1)

        direct_input.PressKey("SPACE")
        sleep(1)
        direct_input.PressKey("SPACE")



    def run(self):
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()

        method = cv.TM_SQDIFF

        comp_path = "ref_images/fishing_space_bar.jpg"
        comp_img = cv.imread(comp_path, 0)

        stream_img = window.grab_frame()
        stream_gray = cv.cvtColor(stream_img, cv.COLOR_BGR2GRAY)

        result = cv.matchTemplate(comp_img, stream_gray, method)
        mn, _, mnLoc, _ = cv.minMaxLoc(result)
        MPx, MPy = mnLoc

        status = 0 # idle=0, space_bar=1

        if (MPx > target_x - target_thresh and MPx < target_x + target_thresh and MPy > target_y - target_thresh and MPy < target_y + target_thresh):
            status = 1
        else:
            status = 0

        if (actions):
            if (status == 0):
                # idle
                print("idle...")
            elif (status == 1):
                # space bar
                self.actions(1)

        else:
            trows,tcols = comp_img.shape[:2]
            font = cv.FONT_HERSHEY_SIMPLEX
            if (status == 0):
                # idle
                cv.putText(stream_img, "Idle Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)
            elif (status == 1):
                # space bar
                cv.rectangle(stream_img, (MPx, MPy), (MPx + tcols, MPy + trows), (0, 0, 255), 2)
                cv.putText(stream_img, "Space Bar Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)

            cv.imshow("output", stream_img)
            cv.waitKey(0)
            cv.destroyAllWindows()
