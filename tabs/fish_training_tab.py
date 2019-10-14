import os, sys, time, uuid, random
import pyautogui
import cv2 as cv
import numpy as np

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from utils.game_window import GameWindow
import utils.direct_input
import utils.input
from utils.ui_generator import *
from utils.fishing_key_sequence import KeySequenceDetector

class FishTab(QWidget):
    def __init__(self):
        super(FishTab, self).__init__()
        startWorkerButton = createButton("Start Worker", self, 0, 0)
        startWorkerButton.released.connect(self._start_worker_button_handler)
        stopWorkerButton = createButton("Stop Worker", self, 0, 1)
        stopWorkerButton.released.connect(self._stop_worker_button_handler)

        self.thread = StreamThread()

    def _start_worker_button_handler(self):
        self.thread.terminate()
        self.thread.start()

    def _stop_worker_button_handler(self):
        self.thread.terminate()
        print("terminated...")

start_target_x = 574
start_target_y = 263
catch_target_x = start_target_x
catch_target_y = start_target_y - 20
target_thresh = 5
actions = True
output_chars = True
output_folder = "screenshots/failures/"
output_spaces = True
spaces_folder_cast = "ml/keys_loc/space_cast"
spaces_folder_reel = "ml/keys_loc/space_reel"

class StreamThread(QThread):
    reel_state = 2
    def __init__(self):
        super(StreamThread, self).__init__()
        self.keySequenceDetector = KeySequenceDetector()
        self.keySequenceDetector.output = True

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
        print("x: " + str(MPx) + ", y: " + str(MPy))

        status = 0

        if (MPx > start_target_x - target_thresh and MPx < start_target_x + target_thresh and MPy > start_target_y - target_thresh and MPy < start_target_y + target_thresh):
            if (self.reel_state == 2):
                self.reel_state = 1
                spaces_folder = spaces_folder_cast
            else:
                self.reel_state = 2
                spaces_folder = spaces_folder_reel
            if output_spaces:
                if not os.path.exists(spaces_folder):
                    os.makedirs(spaces_folder)
                cv.imwrite(os.path.join(spaces_folder, str(uuid.uuid4()) + '.jpg'), self.stream_img)
            return self.reel_state
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
            print("moving camera")
            pyautogui.move(random.gauss(0, 600), random.gauss(0, 40), duration=random.gauss(2, .1))
        elif (action == 2):
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
            # if (len(keySequence) == 0):
            #     print("writing frame to file as failure")
            #     self.stream_img = self.window.grab_frame()
            #     if not os.path.exists(output_folder):
            #         os.makedirs(output_folder)
            #     file_name = str(uuid.uuid4()) + ".jpg"
            #     cv.imwrite(os.path.join(output_folder, file_name), self.stream_img)
            for key in keySequence:
                self.tapKey(key)
            time.sleep(4)
            self.tapKey(4)

    def sleep(self):
        sleep_time = 0.02 + np.clip(random.gauss(0.04, 0.01), 0, 0.08)
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

    def run(self):
        self.reel_state = 2
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
                    self.actions(1)
                    # break
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
            time.sleep(2)

        print("leaving")
