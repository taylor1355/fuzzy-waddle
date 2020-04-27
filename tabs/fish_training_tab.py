import os, sys, time, uuid, random
import pyautogui
import cv2 as cv
import numpy as np

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from utils.game_window import GameWindow
from utils.direct_input import PressKey, ReleaseKey
import utils.input
from utils.ui_generator import *
from utils.fishing_key_sequence import KeySequenceDetector
from ml.new_ui_keys.classifier import Classifier

class FishTab(QWidget):
    name = "Fish Data"
    def __init__(self):
        super(FishTab, self).__init__()
        startWorkerButton = createButton("Start Worker", self, 0, 0)
        startWorkerButton.released.connect(self._start_worker_button_handler)
        stopWorkerButton = createButton("Stop Worker", self, 0, 1)
        stopWorkerButton.released.connect(self._stop_worker_button_handler)
        self.spaceYTextBox = createTextBox(self, 0, 2)
        self.spaceYTextBox.setText(str(start_target_y))
        setSpaceYButton = createButton("Set Space Y", self, 0, 3)
        setSpaceYButton.released.connect(self._set_space_y_button_handler)
        findSpaceYButton = createButton("Find Space Y", self, 0, 3)
        findSpaceYButton.released.connect(self._find_space_y_button_handler)

        self.thread = StreamThread()

    def getModuleFrom(self, controller):
        pass

    def _start_worker_button_handler(self):
        self.thread.terminate()
        self.thread.start()

    def _stop_worker_button_handler(self):
        self.thread.terminate()
        print("terminated...")

    def _set_space_y_button_handler(self):
        try:
            global start_target_y
            start_target_y = int(self.spaceYTextBox.text())
            print(f'Set space y to {start_target_y}')
        except Exception:
            print(f'Error: could not convert \'{self.spaceYTextBox.text()}\' to int')

    def _find_space_y_button_handler(self):
        comp_path = "resources/fishing_space_bar.jpg"
        comp_img = cv.imread(comp_path, 0)
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()
        for i in range(20):
            img = window.grab_frame()
            img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            method = cv.TM_SQDIFF
            result = cv.matchTemplate(comp_img, img_gray, method)
            mn, _, mnLoc, _ = cv.minMaxLoc(result)
            MPx, MPy = mnLoc
            print("x: " + str(MPx) + ", y: " + str(MPy))
            time.sleep(0.1)


press_keys = True
start_target_x = 588
start_target_y = 197
catch_target_x = -100
catch_target_y = -100
target_thresh = 5
actions = True
output_chars = True
output_folder = "screenshots/failures/"
output_spaces = False
output_empty = False
spaces_folder_cast = "ml/new_ui_keys/spacebar_cast"
spaces_folder_reel = "ml/new_ui_keys/spacebar_reel"
no_spaces_folder = "ml/new_ui_keys/no_spacebar"
output_result = False
results_folder = "ml/new_ui_keys/results"
key_names = 'W', 'A', 'S', 'D'

output_catch = True
catch_folder = "ml/new_ui_keys/catches"


class StreamThread(QThread):
    reel_state = 2
    def __init__(self):
        super(StreamThread, self).__init__()
        self.keySequenceDetector = KeySequenceDetector()
        self.keySequenceDetector.output = True
        self.classifier = Classifier('./ml/new_ui_keys/')

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
                for i in range(10):
                    pyautogui.move(random.gauss(0, 50), random.gauss(0, 5), duration=random.gauss(0.1, .01))
                    cv.imwrite(os.path.join(spaces_folder, str(uuid.uuid4()) + '.jpg'), self.window.grab_frame())
            return self.reel_state
        elif (MPx > catch_target_x - target_thresh and MPx < catch_target_x + target_thresh and MPy > catch_target_y - target_thresh and MPy < catch_target_y + target_thresh):
            return 2
        else:
            return 0

    def actions(self, action):
        if (action == 1):
            if output_result:
                if not os.path.exists(results_folder):
                    os.makedirs(results_folder)
                if not self.prev_time is None:
                    elap_time = time.time() - self.prev_time
                    with open(results_folder + '/minigame_times.txt', 'a+') as f:
                        f.write(f'{elap_time}\n')
                self.prev_time = time.time()
            PressKey("SPACE")
            print("casting line")
            ReleaseKey("SPACE")
            time.sleep(5)
            # print("moving camera")
            # pyautogui.move(random.gauss(0, 600), random.gauss(0, 40), duration=random.gauss(2, .1))
            if output_empty:
                if not os.path.exists(no_spaces_folder):
                    os.makedirs(no_spaces_folder)
                for i in range(10):
                    pyautogui.move(random.gauss(0, 50), random.gauss(0, 5), duration=random.gauss(0.1, .01))
                    cv.imwrite(os.path.join(no_spaces_folder, str(uuid.uuid4()) + '.jpg'), self.window.grab_frame())
        elif (action == 2):
            PressKey("SPACE")
            print("reeling in")
            ReleaseKey("SPACE")
            time.sleep(1.6 + 0.04)
            PressKey("SPACE")
            print("playing game")
            ReleaseKey("SPACE")
            time.sleep(3.0)
            img = self.window.grab_frame()
            now = time.time()
            keySequence = self.classifier.evaluate_and_save(img, './ml/new_ui_keys/raw')
            print(f'Time to read seq: {time.time()-now}')
            if keySequence is None:
                keySequence = []
            # self.keySequenceDetector.processFrames(2, 2)
            # keySequence = self.keySequenceDetector.getKeySequence()
            print("keys: " + str([key_names[key] for key in keySequence]))
            # time.sleep(1.2)
            # if (len(keySequence) == 0):
            #     print("writing frame to file as failure")
            #     self.stream_img = self.window.grab_frame()
            #     if not os.path.exists(output_folder):
            #         os.makedirs(output_folder)
            #     file_name = str(uuid.uuid4()) + ".jpg"
            #     cv.imwrite(os.path.join(output_folder, file_name), self.stream_img)
            if press_keys:
                for key in keySequence:
                    self.tapKey(key)
            if output_result:
                if not os.path.exists(results_folder):
                    os.makedirs(results_folder)
                img = cv.putText(img, str([key_names[key] for key in keySequence]), (400, 245), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv.imwrite(os.path.join(results_folder, f'{uuid.uuid4()}.jpg'), img)
                if not self.prev_time is None:
                    elap_time = time.time() - self.prev_time
                    with open(results_folder + '/reeling_times.txt', 'a+') as f:
                        f.write(f'{elap_time}\n')
                self.prev_time = time.time()
            time.sleep(6)
            if output_catch:
                if not os.path.exists(catch_folder):
                    os.makedirs(catch_folder)
                cv.imwrite(f'{catch_folder}/{uuid.uuid4()}.jpg', self.window.grab_frame())
            self.tapKey(4)

    def sleep(self):
        sleep_time = 0.03 + np.clip(random.gauss(0.04, 0.015), 0, 0.8)
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
        PressKey(key_string)
        self.sleep()
        ReleaseKey(key_string)
        self.sleep()

    def run(self):
        self.reel_state = 2
        self.window = GameWindow("BLACK DESERT")
        self.window.move_to_foreground()
        self.prev_time = None

        point = self.window.rect.center()
        pyautogui.moveTo(point[0], point[1], duration=2)

        comp_path = "resources/fishing_space_bar.jpg"
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
