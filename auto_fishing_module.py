import sys, os, time
import pyautogui
import cv2 as cv
import numpy as np

from actions import Action
import direct_input
import input

sys.path.append("ml")
from ml.model import Model

start_target_x = 575
start_target_y = 222
catch_target_x = 574
catch_target_y = 205
target_thresh = 5
actions = False

class AutoFishingModule():
    def __init__(self):
        self.isEnabled = True
        self.reelInFishAction = Action(0, self.reelInFish)
        self.castLineAction = Action(0, self.castLine)
        comp_path = "ref_images/fishing_space_bar.jpg"
        self.comp_img = cv.imread(comp_path, 0)

        self.spacebar_model = Model.load("ml/spacebar/spacebar_model.pkl")
        self.spacebar_height, self.spacebar_width = self.spacebar_model.box_size

    def getActions(self, frame):
        self.lastFrame = frame
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        method = cv.TM_SQDIFF
        result = cv.matchTemplate(self.comp_img, frame_gray, method)
        mn, _, mnLoc, _ = cv.minMaxLoc(result)
        MPx, MPy = mnLoc

        state = 0
        if (MPx > start_target_x - target_thresh and MPx < start_target_x + target_thresh and MPy > start_target_y - target_thresh and MPy < start_target_y + target_thresh):
            state = 1
        elif (MPx > catch_target_x - target_thresh and MPx < catch_target_x + target_thresh and MPy > catch_target_y - target_thresh and MPy < catch_target_y + target_thresh):
            state = 2

        show_image = True
        if show_image:
            img = np.array(frame)

            spacebar_region = self.region_of_interest(frame, start_target_x, start_target_y, self.spacebar_width, self.spacebar_height)
            spacebar_detected = self.spacebar_model.predict(spacebar_region)

            font = cv.FONT_HERSHEY_SIMPLEX
            if (not spacebar_detected):
                cv.putText(img, "Idle Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)
            else:
                cv.putText(img, "Space Bar Detected", (180, 25), font, 0.8, (255, 0, 0), 2, cv.LINE_AA)

            print(str(start_target_x) + " " + str(start_target_y))
            cv.rectangle(img, (start_target_x, start_target_y), (start_target_x + self.spacebar_width, start_target_y + self.spacebar_height), (0, 0, 255), 2)
            cv.imshow("output", img)
            cv.waitKey(0)
            cv.destroyAllWindows()

        if state == 1:
            return [self.castLineAction]
        elif state == 2:
            return [self.reelInFishAction]
        else:
            return []

    def region_of_interest(self, img, min_x, min_y, width, height):
        return img[min_y : min_y+height, min_x : min_x+width]

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
