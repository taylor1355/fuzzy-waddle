import sys, time
import pyautogui
import cv2 as cv
import numpy as np

from utils.game_window import GameWindow
from modules.auto_fishing_module import AutoFishingModule

from PySide2.QtCore import QThread

class MasterModule(QThread):
    def __init__(self):
        super(MasterModule, self).__init__()
        self.isActive = False
        self.autoFishingModule = AutoFishingModule()
        self.modules = [self.autoFishingModule]

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
            for module in self.modules:
                if module.isEnabled:
                    actions = module.getActions(frame)
            # process queue
            for action in actions:
                if action:
                    action.execute()
                else:
                    print("idle...")
                    time.sleep(1)