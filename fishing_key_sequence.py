import os, sys, time, uuid
import pyautogui
import cv2 as cv
import numpy as np

from game_window import GameWindow

sys.path.append("ml")
from ml.model import Model

pixel_thresh = 140
output = True
output_amnt = 8
output_folder = "ml/keys_2/data/"
output_border = True
output_overlay = False
output_pixel_border = 5
output_last_folder = output_folder + "last/"

class KeySequenceDetector():
    def __init__(self):
        self.show_image = False
        self.show_border = False
        self.show_overlay = False

        self.start_x, self.start_y, self.w, self.h = 0, 0, 0, 0

        self.keys_model = Model.load("ml/keys_2/keys_model.pkl")

    def processFrames(self, pos=1, read_time=1):
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()

        print("grabbing frames for " + str(read_time) + " seconds")

        mask_path = "ref_images/combined_key_color.tiff"
        mask = cv.imread(mask_path, 1)

        show_amnt = 6

        key_detectors = []
        for i in range(pos):
            key_detectors.append(KeyDetectorDiff(mask, i))

        cut_time = time.time() + read_time

        f = 0
        while time.time() <= cut_time:
            f += 1
            print("procressing frame " + str(f))
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
            h, w = mask.shape[0] + 2*output_pixel_border, mask.shape[1] + 2*output_pixel_border
            for c in range(output_amnt):
                out_file = np.zeros((h, w, 3), np.uint8)
                out_file[:, :] = color_frame[key_detectors[0].y+max_y-output_pixel_border:key_detectors[0].y+max_y+h-output_pixel_border, key_detectors[0].x+max_x+(c * di)-output_pixel_border:key_detectors[0].x+max_x+(c * di)+w-output_pixel_border]
                # print("writing to file")
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                file_name = str(uuid.uuid4()) + ".jpg"
                cv.imwrite(os.path.join(output_folder, file_name), out_file)
            out_file = np.zeros((key_detectors[0].h+key_detectors[0].dy, key_detectors[0].w+key_detectors[0].dx, 3), np.uint8)
            out_file[:, :] = color_frame[key_detectors[0].y:key_detectors[0].y+h+key_detectors[0].dy-(2*output_pixel_border), key_detectors[0].x:key_detectors[0].x+w+key_detectors[0].dx-(2*output_pixel_border)]

            h, w = mask.shape[0], mask.shape[1]
            norm_out = np.copy(out_file)
            inv_out = np.copy(out_file)
            diff_out = np.copy(out_file)
            comb_norm = np.zeros((KeyDetectorDiff.dy, KeyDetectorDiff.dx), np.int16)
            comb_inv = np.zeros((KeyDetectorDiff.dy, KeyDetectorDiff.dx), np.int16)
            for key_detector in key_detectors:
                comb_norm += key_detector.normal_dev_image
                comb_inv += key_detector.inverse_dev_image
            normalized_norm = KeyDetectorDiff.normalize(comb_norm)
            normalized_inv = KeyDetectorDiff.normalize(comb_inv)
            normalized_diff = KeyDetectorDiff.normalize(comb_frame)


            flattened = np.copy(normalized_diff).flatten()
            sorteda = np.argsort(flattened)
            print(sorteda)
            amnt = 20

            perc = 0.7
            for i in range(normalized_norm.shape[0]):
                for j in range(normalized_norm.shape[1]):
                    norm_out[i, j] = (norm_out[i, j] * (1 - perc)) + (normalized_norm[i, j] * perc)
                    inv_out[i, j] = (inv_out[i, j] * (1 - perc)) + (normalized_inv[i, j] * perc)
                    diff_out[i, j] = (diff_out[i, j] * (1 - perc)) + (normalized_diff[i, j] * perc)
            for i in range( len(sorteda) - amnt, len(sorteda) ):
                a = sorteda[i]
                diff_out[int(a/30), int(a)%30] = [0, 0, 255]
            if True:
                for i in range(h):
                    for j in range(w):
                        if output_overlay and mask_red[i, j] > 0:
                            out_file[i + max_y, j + max_x] = [255, 0, 0]
                        if output_border and (i < 2 or i >= h-2 or j < 2 or j >= w-2):
                            out_file[i + max_y, j + max_x] = [0, 0, 255]
            print("writing to file")
            if not os.path.exists(output_last_folder):
                os.makedirs(output_last_folder)
            cv.imwrite(os.path.join(output_last_folder, "masked.tiff"), out_file)
            cv.imwrite(os.path.join(output_last_folder, "norm.tiff"), norm_out)
            cv.imwrite(os.path.join(output_last_folder, "inv.tiff"), inv_out)
            cv.imwrite(os.path.join(output_last_folder, "diff.tiff"), diff_out)
            cv.imwrite(os.path.join(output_last_folder, "frame.jpg"), color_frame)

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
            if key[0] < 0:
                return keySequence
            else:
                keySequence.append(key[0])
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
