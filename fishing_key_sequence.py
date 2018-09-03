import os, sys, time, uuid
import pyautogui
import cv2 as cv
import numpy as np

from game_window import GameWindow

sys.path.append("ml")
from ml.model import Model

pixel_thresh = 140
output = True
output_amnt = 6
output_folder = "ml/keys/data/"
output_border = True
output_overlay = False

class KeySequenceDetector():
    def __init__(self):
        self.show_image = False
        self.show_border = False
        self.show_overlay = False

        self.start_x, self.start_y, self.w, self.h = 0, 0, 0, 0

        self.keys_model = Model.load("ml/keys/keys_model.pkl")

    def processFrames(self, pos=1, amnt=1):
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()

        print("grabbing " + str(amnt) + " frames")

        mask_path = "ref_images/combined_key_color.tiff"
        mask = cv.imread(mask_path, 1)

        show_amnt = 5

        key_detectors = []
        for i in range(pos):
            key_detectors.append(KeyDetectorDiff(mask, i))

        for f in range(amnt):
            print("procressing frame " + str(f+1))
            color_frame = window.grab_frame()
            frame = cv.cvtColor(color_frame, cv.COLOR_BGR2GRAY)
            for key_detector in key_detectors:
                key_detector.processFrame(frame)

        comb_frame = np.zeros((KeyDetectorDiff.dy, KeyDetectorDiff.dx), np.int16)
        for key_detector in key_detectors:
            comb_frame += key_detector.getDifferenceImage()

        _, max_x, max_y = KeyDetectorDiff.getMaxAndPos(comb_frame)
        self.start_x, self.start_y = key_detectors[0].x + max_x, key_detectors[0].y + max_y
        self.w, self.h = mask.shape[1], mask.shape[0]
        self.last_frame = color_frame

        if output:
            di = KeyDetectorDiff.di
            max, max_x, max_y = KeyDetectorDiff.getMaxAndPos(comb_frame)
            mask_red = mask[:, :, 2] > pixel_thresh
            h, w = mask.shape[0], mask.shape[1]
            for c in range(output_amnt):
                out_file = np.zeros((h, w, 3), np.uint8)
                out_file[:, :] = color_frame[key_detectors[0].y+max_y:key_detectors[0].y+max_y+h, key_detectors[0].x+max_x+(c * di):key_detectors[0].x+max_x+(c * di)+w]
                # print("writing to file")
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                file_name = str(uuid.uuid4()) + ".jpg"
                cv.imwrite(os.path.join(output_folder, file_name), out_file)
            out_file = np.zeros((key_detectors[0].h+key_detectors[0].dy, key_detectors[0].w+key_detectors[0].dx, 3), np.uint8)
            out_file[:, :] = color_frame[key_detectors[0].y:key_detectors[0].y+h+key_detectors[0].dy, key_detectors[0].x:key_detectors[0].x+w+key_detectors[0].dx]
            if True:
                for i in range(h):
                    for j in range(w):
                        if output_overlay and mask_red[i, j] > 0:
                            out_file[i + max_y, j + max_x] = [255, 0, 0]
                        if output_border and (i < 2 or i >= h-2 or j < 2 or j >= w-2):
                            out_file[i + max_y, j + max_x] = [0, 0, 255]
            print("writing to file")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            file_name = str(uuid.uuid4()) + ".jpg"
            cv.imwrite(os.path.join(output_folder, file_name), out_file)

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
        x, y, w, h = self.start_x + pos * 35, self.start_y, self.w, self.h
        img = np.zeros((self.h, self.w, 3), np.uint8)
        img[:, :] = frame[y:y+h, x:x+w]
        return img

    def getKeySequence(self):
        keySequence = []
        hasCharacters = True
        for pos in range(8):
            img = self.getCharImage(pos)
            key = self.keys_model.predict(img)
            if key < 0:
                return keySequence
            else:
                keySequence.append(key)
        return keySequence


class KeyDetectorDiff():
    x, y, dx, dy, di = 463, 380, 30, 30, 35
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
        # print("min: " + str(min) + ", max: " + str(max))
        div = (max - min) / 255
        # print(div)
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
