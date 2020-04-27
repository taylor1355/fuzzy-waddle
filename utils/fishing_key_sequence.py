import os, sys, time, uuid
import pyautogui
import cv2 as cv
import numpy as np
import csv

from utils.game_window import GameWindow
from ml.model import Model

pixel_thresh = 140
output_amnt = 8
output_folder = "ml/new_ui_keys/raw/"
output_border = True
output_overlay = False
output_pixel_border = 5
output_last_folder = output_folder + "last/"
csv_name = "info.csv"

class KeySequenceDetector():
    def __init__(self):
        self.show_image = False
        self.show_border = False
        self.show_overlay = False
        self.save_full_image = False
        self.output = False

        self.start_x, self.start_y, self.w, self.h = 0, 0, 0, 0

        self.keys_model = Model.load("ml/keys/keys_model.pkl")

    def processFrames(self, pos=1, read_time=1):
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()

        print("grabbing frames for " + str(read_time) + " seconds")

        mask_path = "resources/combined_key_color.tiff"
        mask = cv.imread(mask_path, 1)

        show_amnt = 6

        key_detectors = []
        for i in range(pos):
            key_detectors.append(KeyDetectorDiff(mask, i))

        cut_time = time.time() + read_time

        f = 0
        frames = []
        while time.time() <= cut_time:
            f += 1
            print("procressing frame " + str(f))
            color_frame = window.grab_frame()
            frame = cv.cvtColor(color_frame, cv.COLOR_BGR2GRAY)
            frames.append(color_frame)
            for key_detector in key_detectors:
                key_detector.processFrame(frame)

        comb_frame = np.zeros((KeyDetectorDiff.dy, KeyDetectorDiff.dx), np.int16)
        for key_detector in key_detectors:
            comb_frame += key_detector.getDifferenceImage()

        _, max_x, max_y = KeyDetectorDiff.getMaxAndPos(comb_frame)
        self.start_x, self.start_y = key_detectors[0].x + max_x, key_detectors[0].y + max_y
        self.w, self.h = mask.shape[1], mask.shape[0]
        self.last_frame = color_frame

        if self.output:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            out_dir = output_folder + str(uuid.uuid4())
            print("saving to " + out_dir)
            os.makedirs(out_dir)
            for i in range(1):#len(frames)):
                cv.imwrite(os.path.join(out_dir, "frame" + str(i) + ".jpg"), frames[i])

            di = KeyDetectorDiff.di
            max, max_x, max_y = KeyDetectorDiff.getMaxAndPos(comb_frame)
            keySequence = self.getKeySequence()

            with open(out_dir + "/" + csv_name, mode="w") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([max_x, max_y, keySequence])

        if self.show_image:
            di = KeyDetectorDiff.di
            mask_red = mask[:, :, 2] > pixel_thresh
            h, w = mask.shape[0], mask.shape[1]
            for c in range(show_amnt):
                for i in range(h):
                    for j in range(w):
                        if self.show_overlay and mask_red[i, j] > 0:
                            color_frame[key_detectors[0].y + i + max_y, key_detectors[0].x + j + max_x + (c * di)] = [255, 0, 0]
                        if self.show_border and (i < 2 or i >= h-2 or j < 2 or j >= w-2):
                            color_frame[key_detectors[0].y + i + max_y, key_detectors[0].x + j + max_x + 35 * c] = [0, 0, 255]
            cv.imshow("frame", color_frame)
            cv.waitKey(0)
            cv.destroyAllWindows()

    def getCharImage(self, pos):
        frame = self.last_frame
        x, y, w, h = self.start_x + pos * 37, self.start_y, self.w, self.h
        img = np.zeros((self.h, self.w, 3), np.uint8)
        img[:, :] = frame[y:y+h, x:x+w]
        return img

    def getKeySequence(self):
        keySequence = []
        hasCharacters = True
        for pos in range(10):
            img = self.getCharImage(pos)
            key = self.keys_model.predict(img)
            if key[0] < 0:
                return keySequence
            else:
                keySequence.append(key[0])
        return keySequence


class KeyDetectorDiff():
    x, y, dx, dy, di = 463, 380, 30, 30, 37
    amnt = 1

    def __init__(self, mask, pos):
        self.mask = mask
        self.x += pos * self.di
        self.w, self.h = self.mask.shape[1], self.mask.shape[0]
        self.cntr = 0

        self.normal_kernel = np.zeros((self.h, self.w), np.uint8)
        self.mask_red = mask[:, :, 2] > pixel_thresh
        self.normal_kernel[self.mask_red] = self.amnt

        self.inverse_kernel = np.zeros((self.h, self.w), np.uint8)
        self.mask_green = mask[:, :, 1] > pixel_thresh
        self.inverse_kernel[self.mask_green] = self.amnt

        self.normal_avg_image = np.zeros((self.dx, self.dy), np.uint8)
        self.normal_dev_image = np.zeros((self.dx, self.dy), np.int16)
        self.inverse_dev_image = np.zeros((self.dy, self.dx), np.int16)

    def processFrame(self, frame):
        for i in range(0, self.dy):
            for j in range(0, self.dx):
                self.normal_avg_image[i, j] = int(np.sum(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w]*self.normal_kernel[:, :]) / 255)
        for i in range(0, self.dy):
            for j in range(0, self.dx):
                self.normal_dev_image[i, j] = int(np.sum(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w]*self.normal_kernel[:, :]-self.normal_avg_image[i, j]) / 255)
        for i in range(self.dx):
            for j in range(self.dy):
                self.inverse_dev_image[i, j] = int(np.sum(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w]*self.inverse_kernel[:, :]-self.normal_avg_image[i, j]) / 255)
        self.cntr += 1

    def getDifferenceImage(self):
        if self.cntr > 0:
            difference_image = np.zeros((self.dy, self.dx), np.int16)
            for i in range(self.dy):
                for j in range(self.dx):
                    difference_image[i, j] = int(self.inverse_dev_image[i, j]) - int(self.normal_dev_image[i, j]) + (127 * self.cntr)
            return difference_image

    def normalize(frame):
        normalized_frame = np.zeros((frame.shape[0], frame.shape[1]), np.uint8)
        min, max = np.min(frame), np.max(frame)
        div = (max - min) / 255
        normalized_frame[:, :] = (frame[:, :] - min) / div
        return normalized_frame

    def getMaxAndPos(frame):
        max, max_x, max_y = 0, 0, 0
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                if frame[i, j] > max:
                    max = frame[i, j]
                    max_y, max_x = i, j
        return max, max_x, max_y
