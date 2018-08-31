import os, sys, time
import pyautogui
import cv2 as cv
import numpy as np

import utils
from controller_thread import MainController

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
