from enum import Enum
import sys, os, time
import pyautogui
import cv2 as cv
import numpy as np
import random
import uuid

from utils.game_window import GameWindow
from utils.direct_input import PressKey, ReleaseKey
from ml.key_classifier import Classifier
from actions import Action

class State():
    LINE_OUT_OF_WATER = 1
    LINE_IN_WATER = 2

class AutoFishingModule():

    space_icon_x = 588
    space_icon_ys = 197, 192
    space_icon_thresh = 2
    key_names = 'W', 'A', 'S', 'D'

    def __init__(self):
        self.isEnabled = False

        self.reelInFishAction = Action(0, self.reelInFish)
        self.castLineAction = Action(0, self.castLine)
        self.classifier = Classifier('./ml/')
        self.comp_img = cv.imread('resources/fishing_space_bar.jpg', 0)
        self.window = GameWindow("BLACK DESERT")
        self.colorGrabber = ColorGrabber()

        self.outputColors = False
        self.outputKeys = False
        self.swapRods = False
        self.rodCharSeq = ''
        self.rodSwapThresh = 5

        self.collectAll = True
        self.discardBlue = False
        self.discardGreen = False
        self.collectUnknowns = False

        self.reset()


    def reset(self):
        self.last_frame = None
        self.state = State.LINE_OUT_OF_WATER
        self.rodCatchCount = 0


    def getActions(self, frame):
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        method = cv.TM_SQDIFF
        result = cv.matchTemplate(self.comp_img, frame_gray, method)
        mn, _, mnLoc, _ = cv.minMaxLoc(result)
        MPx, MPy = mnLoc
        print("x: " + str(MPx) + ", y: " + str(MPy))

        if (abs(MPx - self.space_icon_x) < self.space_icon_thresh and (abs(MPy - space_icon_y) < self.space_icon_thresh for space_icon_y in self.space_icon_ys)):
            if (self.state == State.LINE_OUT_OF_WATER):
                return [self.castLineAction,]
            else:
                return [self.reelInFishAction,]
        return []


    def reelInFish(self):
        PressKey("SPACE")
        print("reeling in")
        ReleaseKey("SPACE")
        time.sleep(1.6 + 0.04)
        PressKey("SPACE")
        print("playing game")
        ReleaseKey("SPACE")
        time.sleep(3.0)
        img = self.window.grab_frame()
        if self.outputKeys:
            keySequence = self.classifier.evaluate_and_save(img, './ml/new_ui_keys/raw')
        else:
            keySequence = self.classifier.evaluate(img)
        if keySequence is None:
            keySequence = []
        print("keys: " + str([self.key_names[key] for key in keySequence]))
        for key in keySequence:
            self.tapKey(key)
        time.sleep(6)
        # decide wether to grab or not
        if self.collectAll:
            print('shortcutted')
            self.tapKey(4)
        else:
            img = self.window.grab_frame()
            if self.outputColors:
                folder = './ml/new_ui_keys/catches'
                if not os.path.exists(folder):
                    os.makedirs(folder)
                cv.imwrite(f'{folder}/{uuid.uuid4()}.tiff', img)
            if self.colorGrabber.evaluate(img, self.discardBlue, self.discardGreen, self.collectUnknowns):
                self.tapKey(4)
        self.rodCatchCount += 1
        if self.swapRods and self.rodCatchCount >= self.rodSwapThresh:
            print('cycling rods')
            time.sleep(0.5)
            for char in self.rodCharSeq:
                self.tapChar(char)
            self.rodCatchCount = 0
        self.state = State.LINE_OUT_OF_WATER


    def castLine(self):
        PressKey("SPACE")
        print("casting line")
        ReleaseKey("SPACE")
        time.sleep(5)
        self.state = State.LINE_IN_WATER


    def key_sleep(self):
        sleep_time = 0.04 + np.clip(random.gauss(0.04, 0.015), 0, 0.8)
        time.sleep(sleep_time)


    def tapChar(self, char):
        PressKey(char)
        self.key_sleep()
        ReleaseKey(char)
        self.key_sleep()


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
        self.key_sleep()
        ReleaseKey(key_string)
        self.key_sleep()


class Colors():
    GOLD = 1
    BLUE = 2
    GREEN = 3
    OTHER = 4

class ColorGrabber():

    item_x, item_y, dx = 11, 61, 54
    back_colors = (
        (Colors.GOLD, (197, 71, 13)),
        (Colors.BLUE, (53.5, 115.5, 188)),
        (Colors.GREEN, (188, 92, 125)),
    )

    def __init__(self):
        self.comp_img = cv.imread('./resources/item_box.jpg', 0)
        self.color_mask = cv.imread('./resources/item_color_mask3.tiff', 0)
        self.relic_img = cv.imread('./resources/relic_shard.jpg', 1) * 1.0

    def evaluate(self, frame, discardBlue, discardGreen, keepUnknowns):
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        result = cv.matchTemplate(self.comp_img, frame_gray, cv.TM_SQDIFF)
        mn, _, mnLoc, _ = cv.minMaxLoc(result)
        x, y = mnLoc

        img = frame[y:y+self.comp_img.shape[0], x:x+self.comp_img.shape[1]]

        img_colors = []
        diffs = []
        shouldPass = True
        for i in range(4):
            color = [0, 0, 0]
            diffs.append(np.sum(np.square(self.relic_img - img[61:61+45,11+i*self.dx:11+i*self.dx+45])))
            for c in range(3):
                color[c] = np.sum(self.color_mask * img[61:61+45,11+i*self.dx:11+i*self.dx+45,c]) / 176
            print(color)

            if(abs(color[0] - color[1]) < 10 and abs(color[0] - color[2]) < 10):
                print('Other')
                if(keepUnknowns):
                    shouldpass = True
            elif(color[2] > color[1] and color[2] > color[0]):
                print('blue')
                if discardBlue:
                    shouldPass = False
                else:
                    return True
            elif(color[0]/color[2] > 4):
                print('gold')
                return True
            elif(color[0] > color[1] and color[0] > color[2] and color[2] < color[1]):
                print('red')
                return True
            elif(color[0] > color[2] and color[2] > color[1]):
                print('green')
                if discardGreen:
                    shouldPass = False
                else:
                    return True
            else:
                break


        # check to see if it is relic
        if min(diffs) < 1000000:
            print('relic')
            return True
        print(f'defaulting, {shouldPass and keepUnknowns}')
        return shouldPass and keepUnknowns
