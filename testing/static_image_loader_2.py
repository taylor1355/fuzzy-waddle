import os, sys, time
import pyautogui
import cv2 as cv
import numpy as np

sys.path.append('ml')
from ml.model import Model

target_x = 574
target_y = 240
target_thresh = 3
pixel_thresh = 140

class KeyDetectorMLScraper():
    x, y, dx, dy, di = 463, 380, 30, 30, 35
    mldx, mldy, mlw, mlh = -14, -7, 370, 85
    amnt = 1

    def __init__(self, mask, pos):
        self.mask = mask
        self.x += pos * self.di
        self.w, self.h = self.mask.shape[1], self.mask.shape[0]
        self.cntr = 0

        self.normal_kernel = np.zeros((self.h, self.w), np.uint16)
        self.mask_red = mask[:, :, 2] > pixel_thresh
        self.normal_kernel[self.mask_red] = self.amnt

        self.inverse_kernel = np.zeros((self.h, self.w), np.uint16)
        self.mask_green = mask[:, :, 1] > pixel_thresh
        self.inverse_kernel[self.mask_green] = self.amnt

        self.normal_image = np.zeros((self.dx, self.dy), np.uint16)
        self.inverse_image = np.zeros((self.dy, self.dx), np.uint16)

    def processFrame(self, frame):
        for i in range(0, self.dy):
            for j in range(0, self.dx):
                self.normal_image[i, j] += int(np.sum(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w]*self.normal_kernel[:, :]) / 255)
        for i in range(self.dx):
            for j in range(self.dy):
                self.inverse_image[i, j] += int(np.sum(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w]*self.inverse_kernel[:, :]) / 255)
        self.cntr += 1

    def getDifferenceImage(self):
        if self.cntr > 0:
            difference_image = np.zeros((self.dy, self.dx), np.int16)
            for i in range(self.dy):
                for j in range(self.dx):
                    difference_image[i, j] = int(self.normal_image[i, j]) - int(self.inverse_image[i, j]) + (127 * self.cntr)
            return difference_image

    def normalize(frame):
        normalized_frame = np.zeros((frame.shape[0], frame.shape[1]), np.uint8)
        min, max = np.min(frame), np.max(frame)
        print("min: " + str(min) + ", max: " + str(max))
        div = (max - min) / 255
        print(div)
        normalized_frame[:, :] = (frame[:, :] - min) / div
        return normalized_frame

    def mlCrop(self, frame):
        cx, cy, cw, ch = self.x + self.mldx-5, self.y + self.mldy-5, self.mlw + self.dx+10, self.mlh + self.dy+10
        new_frame = np.zeros((ch, cw, 3), np.uint8)
        for i in range(ch):
            for j in range(cw):
                new_frame[i][j] = frame[i+cy][j+cx]
        return new_frame

    # def getMaxAndPos(self):
    #     max, max_x, max_y = 0, 0, 0
    #         for j in range(self.dx):
    #             if difference_image[i, j] > max:
    #                 max = difference_image[i, j]
    #                 max_y, max_x = i, j
    #     return max, max_x, max_y
    def getMaxAndPos(frame):
        max, max_x, max_y = 0, 0, 0
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                if frame[i, j] > max:
                    max = frame[i, j]
                    max_y, max_x = i, j
        return max, max_x, max_y




class Runs:
    def run1():
        mask_path = "resources/combined_key_color.tiff"
        mask = cv.imread(mask_path, 1)
        window_path = "screenshots/keys_img001.jpg"
        frame = cv.imread(window_path, 1)
        frame_gray = cv.imread(window_path, 0)

        keyDet = KeyDetectorMLScraper(mask, 0)
        keyDet.processFrame(frame_gray)
        _, mx, my = KeyDetectorMLScraper.getMaxAndPos(keyDet.getDifferenceImage())
        frame[my+KeyDetectorMLScraper.y][mx+KeyDetectorMLScraper.x] = [0, 0, 255]
        frame[KeyDetectorMLScraper.y][KeyDetectorMLScraper.x] = [255, 0, 0]


        mldx, mldy, w, h = -14, -7, 370, 85
        x, y = mx+KeyDetectorMLScraper.x + mldx, my+KeyDetectorMLScraper.y + mldy
        # y, x, h, w = 381, 454, 85, 370
        # dx1 = KeyDetectorMLScraper.x+mx - x
        # dy1 = KeyDetectorMLScraper.y+my - y
        # print (dx1)
        # print (dy1)
        # endx, endy = mx+KeyDetectorMLScraper.x - dx1, my+KeyDetectorMLScraper.y - dy1
        # frame[endy][endx] = [0, 0, 0]
        cropped_frame = np.zeros((h, w, 3), np.uint8)
        for i in range(h):
            for j in range(w):
                cropped_frame[i][j] = frame[i+y][j+x]

        scale = 3
        cv.imshow("cropped", cv.resize(cropped_frame, (w*scale, h*scale)) )
        cv.imshow("frame", frame)
        mlframe = keyDet.mlCrop(frame)
        cv.imshow("mlframe", cv.resize(mlframe, (w*scale, h*scale)) )

        cv.waitKey(0)
        cv.destroyAllWindows()



if __name__ == "__main__":
    Runs.run1()
