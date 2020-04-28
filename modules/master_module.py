import sys, time
import pyautogui
import cv2 as cv
import numpy as np
from queue import PriorityQueue

from utils.game_window import GameWindow
from modules.auto_fishing_module import AutoFishingModule

from PySide2.QtCore import QThread

class MasterModule(QThread):
    def __init__(self):
        super(MasterModule, self).__init__()
        self.isActive = False
        self.autoFishingModule = AutoFishingModule()
        self.modules = [self.autoFishingModule]
        self.actions = PriorityQueue()

    def __del__(self):
        self.wait()

    def quit(self):
        self.isActive = False

    def run(self):
        self.isActive = True

        for module in self.modules:
            module.reset()

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
                    for action in module.getActions(frame):
                        self.actions.put(action)
            # process queue
            while not self.actions.empty():
                self.actions.get().execute()
                if not self.isActive:
                    break
            print("sleeping...")
            for i in range(20):
                if not self.isActive:
                    break
                time.sleep(0.1)
        print('main thread stopped')