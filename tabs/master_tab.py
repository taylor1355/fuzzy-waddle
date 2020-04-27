import os, sys, time, threading
import pyautogui
import cv2 as cv
import numpy as np

from utils.ui_generator import *
from pynput import keyboard

from modules.master_module import MasterModule

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class MasterTab(QWidget):
    def __init__(self):
        super(MasterTab, self).__init__()

        self.startStopButton = createButton("Start", self, 0, 0)
        self.startStopButton.released.connect(self._start_stop_button_handler)

        self.terminateButton = createButton("Terminate", self, 1, 0)
        self.terminateButton.released.connect(self._terminate_button_handler)

        self.controllerLabel = createLabelLText("Ready", self, 0, 1)

        # self.isControllerActive = False
        self.controller = MasterModule()
        self.connect(self.controller, SIGNAL("finished()"), self._controller_finished_handler)

        print('attempting to launch thread...')
        self.thread = threading.Thread(target=KeyboardListener.start_listener_thread, args=(self,))
        self.thread.start()

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
        self.controllerLabel.setText("Ready")
        self.startStopButton.setText("Start")
        self.controller.isActive = False
        print('terminating...')

    def _controller_finished_handler(self):
        self.controllerLabel.setText("Ready")
        self.startStopButton.setText("Start")

class KeyboardListener():
    def start_listener_thread(masterTab):
        KeyboardListener.masterTab = masterTab
        print('thread started!!!')
        with keyboard.Listener(on_release=KeyboardListener._on_release) as listener:
            listener.join()

    def _on_release(key):
        if key == keyboard.Key.end:
            print('stopping from key press')
            KeyboardListener.masterTab.controller.terminate()
            KeyboardListener.masterTab.controllerLabel.setText("Ready")
            KeyboardListener.masterTab.startStopButton.setText("Start")