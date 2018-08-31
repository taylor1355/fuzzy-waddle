import os, sys, time
import pyautogui
import cv2 as cv
import numpy as np

import utils
from actions import Action
import direct_input
import input

from game_window import GameWindow
# from home_tab import HomeModule
# from energy_tab import EnergyModule
# from stream_test_tab import StreamModule
from auto_fishing_tab import AutoFishingModule

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class ControllerTab(QWidget):
    def __init__(self):
        super(ControllerTab, self).__init__()

        self.startStopButton = utils.createButton("Start", self, 0, 0)
        self.startStopButton.released.connect(self._start_stop_button_handler)

        self.terminateButton = utils.createButton("Terminate", self, 1, 0)
        self.terminateButton.released.connect(self._terminate_button_handler)

        self.controllerLabel = utils.createLabelLText("Sleeping", self, 0, 1)

        # self.isControllerActive = False
        self.controller = MainController()
        self.connect(self.controller, SIGNAL("finished()"), self._controller_finished_handler)

    def _start_stop_button_handler(self):
        if self.controller.isActive:
            self.controller.quit()
            self.startStopButton.setText("Start")
            self.controllerLabel.setText("Quitting...")
            self.controller.isActive = False
        else:
            self.controller.start()
            self.startStopButton.setText("Stop")
            self.controllerLabel.setText("Running")
            self.controller.isActive = True

    def _terminate_button_handler(self):
        self.controller.terminate()
        self.controllerLabel.setText("Sleeping")
        self.startStopButton.setText("Start")

    def _controller_finished_handler(self):
        self.controllerLabel.setText("Sleeping")
        self.startStopButton.setText("Start")


class MainController(QThread):
    def __init__(self):
        super(MainController, self).__init__()
        self.isActive = False
        self.autoFishingModule = AutoFishingModule()

    def __del__(self):
        self.wait()

    def quit(self):
        self.isActive = False

    def run(self):
        self.isActive = True
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()

        point = window.rect.center()
        pyautogui.moveTo(point[0], point[1], duration=2)
        while self.isActive:
            # grab frame
            frame = window.grab_frame()
            # fill up queue
            actions = self.autoFishingModule.getActions(frame)
            # process queue
            for action in actions:
                if action:
                    action.execute()
                else:
                    print("idle...")
                    time.sleep(1)
            print("sleeping")
            time.sleep(1)
