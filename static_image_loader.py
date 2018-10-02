import os, sys, time
import pyautogui
import cv2 as cv
import numpy as np

sys.path.append("ml")
from ml.model import Model

target_x = 574
target_y = 240
target_thresh = 3
pixel_thresh = 140

class KeyDetector():
    x, y, dx, dy, di = 463, 380, 30, 30, 35
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
                self.normal_dev_image[i, j] = int(np.sum(abs(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w]*self.normal_kernel[:, :]-self.normal_avg_image[i, j])) / 255)
        for i in range(self.dx):
            for j in range(self.dy):
                self.inverse_dev_image[i, j] = int(np.sum(abs(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w]*self.inverse_kernel[:, :]-self.normal_avg_image[i, j])) / 255)
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

class KeyMapper():
    x, y, di = 463, 380, 35
    amnt = 1

    def __init__(self, masks, dx, dy, pos):
        self.masks = masks
        self.x += dx + (pos * self.di)
        self.y += dy

        self.h, self.w = masks[0].shape[0], masks[0].shape[1]
        self.normal_kernels = []
        for k in range(4):
            mask_red = masks[k][:, :, 2] > pixel_thresh
            normal_kernel = np.zeros((self.h, self.w), np.uint8)
            normal_kernel[mask_red] = self.amnt
            self.normal_kernels.append(normal_kernel)

        self.totals = [0, 0, 0, 0]
        for k in range(4):
            for i in range(self.h):
                for j in range(self.w):
                    if self.normal_kernels[k][i, j] > 0:
                        self.totals[k] += 1

        self.char_vals = [0, 0, 0, 0]

        self.cntr = 0

    def processFrame(self, frame):
        for k in range(4):
            val = np.sum(frame[self.y:self.y+self.h, self.x:self.x+self.w]*self.normal_kernels[k][:, :]) / self.totals[k]
            diff = np.sum(abs(frame[self.y:self.y+self.h, self.x:self.x+self.w]*self.normal_kernels[k][:, :] - val)) / self.totals[k]
            self.char_vals[k] += diff
        self.cntr += 1

    def getKey(self):
        if self.cntr == 0:
            return -1
        min = self.char_vals[0]
        min_pos = 0
        for i in range(1, 4):
            if self.char_vals[i] < min:
                min = self.char_vals[i]
                min_pos = i
        print(self.char_vals)
        return min_pos


class KeyDetectorDiffColor():
    x, y, dx, dy, di = 463, 380, 30, 30, 35
    amnt = [1, 1, 1]

    def __init__(self, mask, pos):
        self.mask = mask
        self.x += pos * self.di
        self.w, self.h = self.mask.shape[1], self.mask.shape[0]
        self.cntr = 0

        self.normal_kernel = np.zeros((self.h, self.w, 3), np.uint8)
        self.mask_red = mask[:, :, 2] > pixel_thresh
        self.normal_kernel[self.mask_red] = self.amnt

        self.inverse_kernel = np.zeros((self.h, self.w, 3), np.uint8)
        self.mask_green = mask[:, :, 1] > pixel_thresh
        self.inverse_kernel[self.mask_green] = self.amnt

        self.normal_avg_image = np.zeros((self.dx, self.dy, 3), np.uint8)
        self.normal_dev_image = np.zeros((self.dx, self.dy), np.int16)
        self.inverse_dev_image = np.zeros((self.dy, self.dx), np.int16)

    def processFrame(self, frame):
        for i in range(0, self.dy):
            for j in range(0, self.dx):
                for c in range(3):
                    self.normal_avg_image[i, j, c] = int(np.sum(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w, c]*self.normal_kernel[:, :, c]) / 255)
        for i in range(0, self.dy):
            for j in range(0, self.dx):
                self.normal_dev_image[i, j] = int(np.sum(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w, :]*self.normal_kernel[:, :, :]-self.normal_avg_image[i, j, :]) / (3 * 255))
                self.inverse_dev_image[i, j] = int(np.sum(frame[self.y+i:self.y+i+self.h, self.x+j:self.x+j+self.w, :]*self.inverse_kernel[:, :, :]-self.normal_avg_image[i, j, :]) / (3 * 255))
        self.cntr += 1

    def getDifferenceImage(self):
        if self.cntr > 0:
            difference_image = np.zeros((self.dy, self.dx), np.int16)
            for i in range(self.dy):
                for j in range(self.dx):
                    difference_image[i, j] += int(1.2*self.inverse_dev_image[i, j]) - int(0.8*self.normal_dev_image[i, j]) + (127 * self.cntr)
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



class Runs():

    def scale(frame, scale):
        scale = int(scale)
        out = np.zeros((frame.shape[0] * scale, frame.shape[1] * scale, frame.shape[2]), np.uint8)
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                out[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = frame[i, j]
        return out

    def scale_gray(frame, scale):
        scale = int(scale)
        out = np.zeros((frame.shape[0] * scale, frame.shape[1] * scale), np.uint8)
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                out[i*scale:(i+1)*scale, j*scale:(j+1)*scale] = frame[i, j]
        return out

    def run9():
        directory = "screenshots/failures/"
        for filename in os.listdir(directory):
            mask_path = "ref_images/combined_key_color.tiff"
            window_path = "screenshots/failures/failure001.jpg"
            window_path = directory + filename
            mask = cv.imread(mask_path, 1)
            frame = cv.imread(window_path, 0)
            color_frame = cv.imread(window_path)

            key_detector = KeyDetectorDiff(mask, 0)
            new_key_detector = KeyDetectorDiffElim(mask, 0)
            key_detector.processFrame(frame)

            di = 35
            comb_frame = KeyDetectorDiffColor.normalize(key_detector.getDifferenceImage())
            max, max_x, max_y = KeyDetectorDiff.getMaxAndPos(comb_frame)

            thresh = 200
            thresh_mask = comb_frame[:, :] < thresh
            thresh_img = np.copy(comb_frame)
            thresh_img[thresh_mask] = 0

            weighted_img = np.copy(thresh_img)

            h, w = key_detector.h + key_detector.dy, key_detector.w + key_detector.dx
            base_context2 = np.zeros((h, w, 3), np.uint8)
            base_context2[:, :] = color_frame[key_detector.y:key_detector.y+h, key_detector.x:key_detector.x+w]
            cv.rectangle(base_context2, (0, 0), (key_detector.dx, key_detector.dy), (255, 0, 0), 1)
            base_context2[max_y, max_x] = [0, 0, 255]

            keys_model = Model.load("ml/keys/keys_model.pkl")
            h, w = key_detector.h, key_detector.w
            output = np.zeros((30, 30, 3), np.uint8)
            for i in range(30):
                for j in range(30):
                    if (thresh_img[i, j] > thresh):
                        base_context = np.zeros((h, w, 3), np.uint8)
                        base_context[:, :] = color_frame[key_detector.y+i:key_detector.y+h+i, key_detector.x+j:key_detector.x+w+j]
                        v = keys_model.predict_prob(base_context)
                        if (v[0] != -1):
                            output[i, j] = [0, 0, v[1] * 255]
                            weighted_img[i, j] = weighted_img[i, j] * v[1]
                        else:
                            output[i, j] = [v[1] * 255, 0, 0] # output[i, j] = [0, 0, 0]
                            weighted_img[i, j] = 0

            cv.imshow("out", Runs.scale(output, 8))
            cv.imshow("comb_frame", Runs.scale_gray(comb_frame, 8))
            cv.imshow("thresh_img", Runs.scale_gray(thresh_img, 8))
            cv.imshow("weighted_img", Runs.scale_gray(weighted_img, 8))
            cv.imshow("base_context", Runs.scale(base_context2, 8))

            # avg_color = np.zeros((100, 100, 3), np.uint8)
            # avg_color[:, :] = key_detector.normal_avg_image[max_y, max_x]
            # cv.imshow("avg", avg_color)
            #
            norm_dev = KeyDetectorDiffColor.normalize(key_detector.normal_dev_image)
            inv_dev = KeyDetectorDiffColor.normalize(key_detector.inverse_dev_image)
            cv.imshow("norm mask", Runs.scale_gray(norm_dev, 8))
            cv.imshow("inv mask", Runs.scale_gray(inv_dev, 8))
            # cv.imshow("diff mask", Runs.scale_gray(KeyDetectorDiffColor.normalize(comb_frame), 4))
            #
            # h, w = key_detector.h + key_detector.dy, key_detector.w + key_detector.dx
            # base_context = np.zeros((h, w, 3), np.uint8)
            # base_context[:, :] = color_frame[key_detector.y:key_detector.y+h, key_detector.x:key_detector.x+w]
            # norm_context = np.copy(base_context)
            # inv_context = np.copy(base_context)
            # diff_context = np.copy(base_context)
            # cv.rectangle(base_context, (0, 0), (key_detector.dx, key_detector.dy), (255, 0, 0), 1)
            # base_context[max_y, max_x] = [0, 0, 255]
            #
            # perc = 0.7
            # for i in range(norm_dev.shape[0]):
            #     for j in range(norm_dev.shape[1]):
            #         norm_context[i, j] = (norm_context[i, j] * (1 - perc)) + (norm_dev[i, j] * perc)
            #         inv_context[i, j] = (inv_context[i, j] * (1 - perc)) + (inv_dev[i, j] * perc)
            # cv.imshow("norm context", Runs.scale(norm_context, 10))
            # cv.imshow("inv context", Runs.scale(inv_context, 10))
            # cv.imshow("base context", Runs.scale(base_context, 10))
            # color_avgs = key_detector.normal_avg_image
            # color_avgs[max_y, max_x] = [0, 0, 255]
            # cv.imshow("color avgs", Runs.scale(color_avgs, 10))
            #
            # mask_red = mask[:, :, 2] > pixel_thresh
            # h, w = mask.shape[0], mask.shape[1]
            # for i in range(h):
            #     for j in range(w):
            #         if mask_red[i, j] > 0:
            #             color_frame[key_detector.y + i + max_y, key_detector.x + j + max_x] = [255, 0, 0]
            # cv.imshow("frame", color_frame)
            cv.waitKey(0)
        cv.destroyAllWindows()

    def run8():
        mask_path = "ref_images/combined_key_color.tiff"
        window_path = "screenshots/keys_img004.jpg"
        mask = cv.imread(mask_path, 1)
        frame = cv.imread(window_path, 1)
        color_frame = cv.imread(window_path)

        key_detector = KeyDetectorDiffColor(mask, 0)
        key_detector.processFrame(frame)

        di = 35
        comb_frame = key_detector.getDifferenceImage()
        max, max_x, max_y = KeyDetectorDiff.getMaxAndPos(comb_frame)

        avg_color = np.zeros((100, 100, 3), np.uint8)
        avg_color[:, :] = key_detector.normal_avg_image[max_y, max_x]
        cv.imshow("avg", avg_color)

        norm_dev = KeyDetectorDiffColor.normalize(key_detector.normal_dev_image)
        inv_dev = KeyDetectorDiffColor.normalize(key_detector.inverse_dev_image)
        cv.imshow("norm mask", Runs.scale_gray(norm_dev, 10))
        cv.imshow("inv mask", Runs.scale_gray(inv_dev, 10))
        cv.imshow("diff mask", Runs.scale_gray(KeyDetectorDiffColor.normalize(comb_frame), 10))

        h, w = key_detector.h + key_detector.dy, key_detector.w + key_detector.dx
        base_context = np.zeros((h, w, 3), np.uint8)
        base_context[:, :] = color_frame[key_detector.y:key_detector.y+h, key_detector.x:key_detector.x+w]
        norm_context = np.copy(base_context)
        inv_context = np.copy(base_context)
        diff_context = np.copy(base_context)
        cv.rectangle(base_context, (0, 0), (key_detector.dx, key_detector.dy), (255, 0, 0), 1)
        base_context[max_y, max_x] = [0, 0, 255]

        perc = 0.7
        for i in range(norm_dev.shape[0]):
            for j in range(norm_dev.shape[1]):
                norm_context[i, j] = (norm_context[i, j] * (1 - perc)) + (norm_dev[i, j] * perc)
                inv_context[i, j] = (inv_context[i, j] * (1 - perc)) + (inv_dev[i, j] * perc)
        cv.imshow("norm context", Runs.scale(norm_context, 10))
        cv.imshow("inv context", Runs.scale(inv_context, 10))
        cv.imshow("base context", Runs.scale(base_context, 10))
        color_avgs = key_detector.normal_avg_image
        color_avgs[max_y, max_x] = [0, 0, 255]
        cv.imshow("color avgs", Runs.scale(color_avgs, 10))

        mask_red = mask[:, :, 2] > pixel_thresh
        h, w = mask.shape[0], mask.shape[1]
        for i in range(h):
            for j in range(w):
                if mask_red[i, j] > 0:
                    color_frame[key_detector.y + i + max_y, key_detector.x + j + max_x] = [255, 0, 0]
        cv.imshow("frame", color_frame)
        cv.waitKey(0)
        cv.destroyAllWindows()

    def run7():
        mask_path = "ref_images/combined_key_color.tiff"
        window_path = "screenshots/keys_img001.jpg"
        mask = cv.imread(mask_path, 1)
        frame = cv.imread(window_path, 0)
        color_frame = cv.imread(window_path)

        key_detectors = []
        for pos in range(2):
            key_detectors.append(KeyDetectorDiff(mask, pos))
            key_detectors[pos].processFrame(frame)

        img1 = KeyDetectorDiff.normalize(key_detectors[0].normal_dev_image)
        img2 = KeyDetectorDiff.normalize(key_detectors[0].inverse_dev_image)
        img3 = KeyDetectorDiff.normalize(key_detectors[0].getDifferenceImage())

        cv.imshow("n", Runs.scale_gray(img1, 10))
        cv.imshow("i", Runs.scale_gray(img2, 10))
        cv.imshow("d", Runs.scale_gray(img3, 10))

        color_frame1 = np.zeros((key_detectors[0].h + key_detectors[0].dy, key_detectors[0].w + key_detectors[0].dx, 3), np.uint8)
        color_frame2 = np.zeros((key_detectors[0].h + key_detectors[0].dy, key_detectors[0].w + key_detectors[0].dx, 3), np.uint8)
        color_frame3 = np.zeros((key_detectors[0].h + key_detectors[0].dy, key_detectors[0].w + key_detectors[0].dx, 3), np.uint8)

        color_frame1[:, :] = color_frame[key_detectors[0].y:key_detectors[0].y+key_detectors[0].h+key_detectors[0].dy, key_detectors[0].x:key_detectors[0].x+key_detectors[0].w+key_detectors[0].dx]
        color_frame2[:, :] = color_frame[key_detectors[0].y:key_detectors[0].y+key_detectors[0].h+key_detectors[0].dy, key_detectors[0].x:key_detectors[0].x+key_detectors[0].w+key_detectors[0].dx]
        color_frame3[:, :] = color_frame[key_detectors[0].y:key_detectors[0].y+key_detectors[0].h+key_detectors[0].dy, key_detectors[0].x:key_detectors[0].x+key_detectors[0].w+key_detectors[0].dx]

        mask_amnt = 0.7
        img_amnt = 1 - mask_amnt
        for i in range(img1.shape[0]):
            for j in range(img1.shape[1]):
                v = img1[i, j] * mask_amnt
                color_frame1[i, j] = (color_frame[key_detectors[0].y + i, key_detectors[0].x + j] * img_amnt) + [v, v, v]
                v = img2[i, j] * mask_amnt
                color_frame2[i, j] = (color_frame[key_detectors[0].y + i, key_detectors[0].x + j] * img_amnt) + [v, v, v]
                v = img3[i, j] * mask_amnt
                color_frame3[i, j] = (color_frame[key_detectors[0].y + i, key_detectors[0].x + j] * img_amnt) + [v, v, v]
        cv.imshow("normal", Runs.scale(color_frame1, 10))
        cv.imshow("inverse", Runs.scale(color_frame2, 10))
        cv.imshow("difference", Runs.scale(color_frame3, 10))

        di = 35
        comb_frame = np.zeros((KeyDetectorDiff.dy, KeyDetectorDiff.dx), np.int16)
        for key_detector in key_detectors:
            comb_frame += key_detector.getDifferenceImage()
        max, max_x, max_y = KeyDetectorDiff.getMaxAndPos(comb_frame)

        # masks_folder = "ref_images/"
        # masks = [cv.imread(masks_folder + "w_key_color.tiff", 1), cv.imread(masks_folder + "a_key_color.tiff", 1), cv.imread(masks_folder + "s_key_color.tiff", 1), cv.imread(masks_folder + "d_key_color.tiff", 1)]

        # key_mappers = []
        # for i in range(7):
        #     key_mappers.append(KeyMapper(masks, max_x, max_y, i))
        #     key_mappers[i].processFrame(frame)
        # print(key_mappers[0].getKey())

        normal_pixels = np.zeros((mask.shape[0], mask.shape[1], 3), np.uint8)
        inverse_pixels = np.zeros((mask.shape[0], mask.shape[1], 3), np.uint8)

        mask_red = mask[:, :, 2] > pixel_thresh
        mask_green = mask[:, :, 1] > pixel_thresh
        h, w = mask.shape[0], mask.shape[1]
        for c in range(8):
            for i in range(h):
                for j in range(w):
                    if mask_red[i, j] > 0:
                        if c == 0:
                            normal_pixels[i, j] = color_frame[key_detectors[0].y + i + max_y, key_detectors[0].x + j + max_x]
                        color_frame[key_detectors[0].y + i + max_y, key_detectors[0].x + j + max_x + c*di] = [255, 0, 0]
                    elif mask_green[i, j] > 0 and c == 0:
                        inverse_pixels[i, j] = color_frame[key_detectors[0].y + i + max_y, key_detectors[0].x + j + max_x]
            # cv.rectangle(color_frame, (key_detector.x, key_detector.y), (key_detector.x + w + key_detector.dx, key_detector.y + h + key_detector.dy), (255, 0, 0), 2)
        cv.imshow("np", normal_pixels)
        cv.imshow("ip", inverse_pixels)
        cv.imshow("frame", color_frame)
        cv.waitKey(0)
        cv.destroyAllWindows()


    def getMaxAndPos(frame):
        max, max_x, max_y = 0, 0, 0
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                if frame[i, j] > max:
                    max = frame[i, j]
                    max_y, max_x = i, j
        return max, max_x, max_y

    def run6():
        mask_path = "ref_images/combined_key_color.tiff"
        window_path = "screenshots/keys_img001.jpg"

        mask = cv.imread(mask_path, 1)
        frame = cv.imread(window_path, 0)
        color_frame = cv.imread(window_path)

        key_detectors = [KeyDetector(mask, 0), KeyDetector(mask, 1), KeyDetector(mask, 2), KeyDetector(mask, 3), KeyDetector(mask, 4), KeyDetector(mask, 5), KeyDetector(mask, 6), KeyDetector(mask, 7)]
        pre = "screenshots/fish_run/"
        frames = [cv.imread(pre + "s1.jpg", 0), cv.imread(pre + "s2.jpg", 0), cv.imread(pre + "s3.jpg", 0), cv.imread(pre + "s4.jpg", 0), cv.imread(pre + "s5.jpg", 0), cv.imread(pre + "s6.jpg", 0), cv.imread(pre + "s7.jpg", 0), cv.imread(pre + "s8.jpg", 0)]
        color_frame = cv.imread(pre + "s1.jpg", 1)
        weights = [10, 10, 2, 2, 1, 1, 1, 1]
        for frame in frames:
            for key_detector in key_detectors:
                key_detector.processFrame(frame)
        # if key_detector.cntr == 0:
        #     print("Error: no images processed")
        #     return

        frame = key_detectors[0].getDifferenceImage()
        comb_frame = np.zeros((frame.shape[0], frame.shape[1]), np.int16)
        for c in range(8):
            comb_frame += key_detectors[c].getDifferenceImage() * weights[c]
        print("min: " + str(np.min(comb_frame)) + ", max: " + str(np.max(comb_frame)))

        di = 35
        max, max_x, max_y = Runs.getMaxAndPos(comb_frame)
        mask_red = mask[:, :, 2] > pixel_thresh
        h, w = mask.shape[0], mask.shape[1]
        for c in range(8):
            for i in range(h):
                for j in range(w):
                    if mask_red[i, j] > 0:
                        color_frame[key_detectors[0].y + i + max_y, key_detectors[0].x + j + max_x + (c * di)] = [255, 0, 0]
            # cv.rectangle(color_frame, (key_detector.x, key_detector.y), (key_detector.x + w + key_detector.dx, key_detector.y + h + key_detector.dy), (255, 0, 0), 2)
        cv.imshow("frame", color_frame)


        # for i in range(h):
        #     for j in range(w):
        #         mask[i, j] = frame[y + i + max_y, x + j + max_x]
        #
        # cv.imshow("max_orig", mask)
        #
        # max_section = np.zeros((h + dy, w + dx, 3), np.uint8)
        # for i in range(h + dy):
        #     for j in range(w + dx):
        #         max_section[i, j] = frame[y + i, x + j]
        # cv.rectangle(max_section, (max_x, max_y), (max_x + w, max_y + h), (0, 0, 255), 2)
        # cv.rectangle(max_section, (0, 0), (dx, dy), (255, 0, 0), 2)
        # cv.imshow("max_section", max_section)
        #
        # max_normal = np.zeros((h, w, 3), np.uint8)
        # max_inverse = np.zeros((h, w, 3), np.uint8)
        # for i in range(h):
        #     for j in range(w):
        #         if mask_red[i, j] > 0:
        #             max_normal[i, j] = frame[y + i + max_y, x + j + max_x]
        #         elif mask_green[i, j] > 0:
        #             max_inverse[i, j] = frame[y + i + max_y, x + j + max_x]
        # cv.imshow("max_norm", max_normal)
        # cv.imshow("max_inv", max_inverse)
        #


        cv.waitKey(0)
        cv.destroyAllWindows()








    def run5():
        mask_path = "ref_images/w_key_color2.jpg"
        window_path = "screenshots/keys_img002.jpg"

        mask = cv.imread(mask_path, 1)
        window = cv.imread(window_path, 0)

        x, y, dx, dy, w, h, di = 463, 380, 6, 0, mask.shape[1], mask.shape[0], 1
        x += dx
        y += dy
        amnt = 1

        mask_new = np.zeros((h, w), np.uint8)
        mask_red = mask[:, :, 2] > pixel_thresh
        mask_new[mask_red] = amnt

        normal_kernel = np.sum(window[y:y+h, x:x+w]*mask_new[:, :]) / 255
        print("Normal Kernel:")
        print(normal_kernel)
        print("")

        mask_inv = np.zeros((h, w), np.uint8)
        mask_green = mask[:, :, 1] > pixel_thresh
        mask_inv[mask_green] = amnt

        inv_kernelp1 = np.sum(window[y:y+h, x:x+w]*mask_inv[:, :]) / 255
        inv_kernelp2 = inv_kernelp1 * normal_kernel / 255
        print("Inverse Kernel p1:")
        print(inv_kernelp1)
        print("")
        print("Inverse Kernel p2:")
        print(inv_kernelp2)
        print("")
        print("Window:")
        print(window[y:y+h, x:x+w])
        print("")
        print("Mask:")
        print(mask_inv[:, :])

        # diff_image = np.zeros((dy, dx), np.uint8)
        # for i in range(dy):
        #     for j in range(dx):
        #         diff_image[i, j] = np.clip((int(new_image[i, j]) - int(inv_image[i, j]) + 255) / 2, 0, 255)

        # cv.imshow("norm", new_image)
        # cv.imshow("inv", inv_image)
        # cv.imshow("diff", diff_image)

        # max, max_x, max_y = 0, 0, 0
        # for i in range(dy):
        #     for j in range(dx):
        #         if diff_image[i, j] > max:
        #             max = diff_image[i, j]
        #             max_y, max_x = i, j
        #         if inv_image[i, j] < 50:
        #             print("y: " + str(i) + ", x: " + str(j) + ", v: " + str(inv_image[i, j]))
        #
        #
        # for i in range(h):
        #     for j in range(w):
        #         mask[i, j] = window[y + i + max_y, x + j + max_x]
        #
        # cv.imshow("max_orig", mask)
        #
        # max_section = np.zeros((h + dy, w + dx, 3), np.uint8)
        # for i in range(h + dy):
        #     for j in range(w + dx):
        #         max_section[i, j] = window[y + i, x + j]
        # cv.rectangle(max_section, (max_x, max_y), (max_x + w, max_y + h), (0, 0, 255), 2)
        # cv.rectangle(max_section, (0, 0), (dx, dy), (255, 0, 0), 2)
        # cv.imshow("max_section", max_section)
        #
        # max_normal = np.zeros((h, w, 3), np.uint8)
        # max_inverse = np.zeros((h, w, 3), np.uint8)
        # for i in range(h):
        #     for j in range(w):
        #         if mask_red[i, j] > 0:
        #             max_normal[i, j] = window[y + i + max_y, x + j + max_x]
        #         elif mask_green[i, j] > 0:
        #             max_inverse[i, j] = window[y + i + max_y, x + j + max_x]
        # cv.imshow("max_norm", max_normal)
        # cv.imshow("max_inv", max_inverse)
        #
        # for i in range(h):
        #     for j in range(w):
        #         if mask_red[i, j] > 0:
        #             window[y + i + max_y, x + j + max_x] = [255, 0, 0]
        # cv.rectangle(window, (x, y), (x + w + dx, y + h + dy), (255, 0, 0), 2)
        #
        # cv.imshow("window", window)

        # cv.waitKey(0)
        # cv.destroyAllWindows()

    def convolution2d(image, kernel, bias):
        m, n, _ = kernel.shape
        y, x, c = image.shape
        y = y - m + 1
        x = x - n + 1
        new_image = np.zeros((y, x, c))
        for i in range(y):
            for j in range(x):
                new_image[i][j] = np.sum(image[i:i+m, j:j+n]*kernel)/255 + bias
        return new_image

    def run4():
        mask_path = "ref_images/w_key_color2.jpg"
        window_path = "screenshots/keys_img004.jpg"

        mask = cv.imread(mask_path, 1)
        window = cv.imread(window_path, 1)

        orig_x, y, dx, dy, w, h, di = 463, 380, 30, 30, mask.shape[1], mask.shape[0], 1
        box_dx = 35
        # x, y, w, h = 470, 402, mask.shape[1], mask.shape[0]

        # w1, h1 = window.shape[1], window.shape[0]
        for box in range(7):
            x = orig_x + box * box_dx
            amnt = [1, 1, 1]

            mask_new = np.zeros((h, w, 3), np.uint8)
            mask_red = mask[:, :, 2] > pixel_thresh
            mask_new[mask_red] = amnt

            new_image = np.zeros((dx, dy), np.uint8)
            for i in range(0, dy, di):
                for j in range(0, dx, di):
                    new_image[i, j] = np.sum(window[y+i:y+i+h, x+j:x+j+w, :]*mask_new[:, :, :]) / 255

            # mask_inv = np.zeros((h, w, 3), np.uint8)
            # mask_green = mask[:, :, 1] > pixel_thresh
            # mask_inv[mask_green] = amnt
            #
            # inv_image = np.zeros((dy, dx), np.uint8)
            # for i in range(dx):
            #     for j in range(dy):
            #         inv_image[i, j] = np.sum(window[y+i:y+i+h, x+j:x+j+w, :]*mask_inv[:, :, :]) / 255 * new_image[i, j] / 255
            #
            # diff_image = np.zeros((dy, dx), np.uint8)
            # for i in range(dy):
            #     for j in range(dx):
            #         diff_image[i, j] = (int(new_image[i, j]) - int(inv_image[i, j]) + 255) / 2

            # cv.imshow("norm", new_image)
            # cv.imshow("inv", inv_image)
            # cv.imshow("diff", diff_image)

            max, max_x, max_y = 0, 0, 0
            for i in range(dy):
                for j in range(dx):
                    if new_image[i, j] > max:
                        max = new_image[i, j]
                        max_y, max_x = i, j


            # for i in range(h):
            #     for j in range(w):
            #         mask[i, j] = window[y + i + max_y, x + j + max_x]
            #
            # cv.imshow("max_orig", mask)
            #
            # max_section = np.zeros((h + dy, w + dx, 3), np.uint8)
            # for i in range(h + dy):
            #     for j in range(w + dx):
            #         max_section[i, j] = window[y + i, x + j]
            # cv.rectangle(max_section, (max_x, max_y), (max_x + w, max_y + h), (0, 0, 255), 2)
            # cv.rectangle(max_section, (0, 0), (dx, dy), (255, 0, 0), 2)
            # cv.imshow("max_section", max_section)
            #
            # max_normal = np.zeros((h, w, 3), np.uint8)
            # max_inverse = np.zeros((h, w, 3), np.uint8)
            # for i in range(h):
            #     for j in range(w):
            #         if mask_red[i, j] > 0:
            #             max_normal[i, j] = window[y + i + max_y, x + j + max_x]
            #         elif mask_green[i, j] > 0:
            #             max_inverse[i, j] = window[y + i + max_y, x + j + max_x]
            # cv.imshow("max_norm", max_normal)
            # cv.imshow("max_inv", max_inverse)

            for i in range(h):
                for j in range(w):
                    if mask_red[i, j] > 0:
                        window[y + i + max_y, x + j + max_x] = [255, 0, 0]
            # cv.rectangle(window, (x, y), (x + w + dx, y + h + dy), (255, 0, 0), 2)

        cv.imshow("window", window)

        cv.waitKey(0)
        cv.destroyAllWindows()

    def normalize(arr):
        w, h = arr.shape[1], arr.shape[0]
        min, max = arr[0, 0], arr[0, 0]
        for yy in range(h):
            for xx in range(w):
                if arr[yy, xx] > max:
                    max = arr[yy, xx]
                if arr[yy, xx] < min:
                    min = arr[yy, xx]
        div = (max - min) / 255
        for yy in range(h):
            for xx in range(w):
                arr[yy, xx] = (arr[yy, xx] - min) / div
        return arr


    def getStdDevDiff(window, mask, x, y):
        total, cntr = [0, 0, 0], 0
        h, w, _ = mask.shape

        for yy in range(h):
            for xx in range(w):
                if mask[yy, xx, 2] > pixel_thresh:
                    total += window[y + yy, x + xx]
                    cntr += 1

        avg = total / cntr
        dev_sq_total = [0, 0, 0]
        inv_sq_total = [0, 0, 0]

        for yy in range(h):
            for xx in range(w):
                if mask[yy, xx, 2] > pixel_thresh:
                    dev_sq_total += np.square(avg - window[y + yy, x + xx])
                elif mask[yy, xx, 1] > pixel_thresh:
                    inv_sq_total += np.square(avg - window[y + yy, x + xx])

        std_dev = np.sqrt(dev_sq_total / cntr)
        avg_std_dev = (std_dev[0] + std_dev[1] + std_dev[2]) / 3
        inv_dev = np.sqrt(inv_sq_total / cntr)
        avg_inv_dev = (inv_dev[0] + inv_dev[1] + inv_dev[2]) / 3
        return avg_inv_dev - avg_std_dev

    def run3():
        mask_path = "ref_images/w_key_color2.jpg"
        window_path = "screenshots/keys_img004.jpg"

        mask = cv.imread(mask_path, 1)
        window = cv.imread(window_path, 1)

        # x, y, w, h = 465, 395, 30, 32
        x, y, dx, dy, w, h = 463, 380, 30, 30, mask.shape[1], mask.shape[0]

        max, max_x, max_y = 0, 0, 0
        for dyy in range(dy):
            for dxx in range(dx):
                val = Runs.getStdDevDiff(window, mask, dxx + x, dyy + y)
                if (val > max):
                    max = val
                    max_x = dxx
                    max_y = dyy

        print(max)

        a = True
        if a:
            for yy in range(h):
                for xx in range(w):
                    if mask[yy, xx, 2] > pixel_thresh:
                        window[y + yy + max_y, x + xx + max_x] = [255, 0, 0]

            cv.rectangle(window, (x, y), (x + w + dx, y + h + dy), (0, 0, 255), 2)
            cv.imshow("output1", window)
        else:
            for yy in range(h):
                for xx in range(w):
                    if mask[yy, xx, 2] > pixel_thresh or mask[yy, xx, 1] > pixel_thresh:
                        mask[yy, xx] = window[y + yy + max_y, x + xx + max_x]
                    else:
                        mask[yy, xx] = [0, 0, 0]

            cv.imshow("output2", mask)

        cv.waitKey(0)
        cv.destroyAllWindows()







    def run2():
        mask_path = "screenshots/w_key_po1.jpg"
        stream_path = "screenshots/keys_img002.jpg"
        thresh = 127

        mask_img = cv.imread(mask_path, 1)
        stream_img = cv.imread(stream_path, 1)

        x, y, w, h = 465, 395, 30, 32
        total, cntr = [0, 0, 0], 1

        for yy in range(y, y + h):
            for xx in range(x, x + w):
                b, _, _ = mask_img[yy, xx]
                if b > thresh:
                    total += stream_img[yy, xx]
                    cntr += 1

        avg = total / cntr

        print(avg[0])
        print(avg[1])
        print(avg[2])
        print("")

        dev_sq_total = [0, 0, 0]

        for yy in range(y, y + h):
            for xx in range(x, x + w):
                b, _, _ = mask_img[yy, xx]
                if b > thresh:
                    dev_sq_total += np.square(avg - stream_img[yy, xx])
                    mask_img[yy, xx] = stream_img[yy, xx]

        std_dev = np.sqrt(dev_sq_total / cntr)
        print(std_dev[0])
        print(std_dev[1])
        print(std_dev[2])
        print("")
        avg_std_dev = (std_dev[0] + std_dev[1] + std_dev[2]) / 3
        print("avg std dev: " + str(avg_std_dev))

        cv.rectangle(mask_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv.imshow("output", mask_img)

        frame = stream_img
        write = False
        if (write):
            write_dir = "output"
            if not os.path.exists(write_dir):
                os.makedirs(write_dir)
            cv.imwrite(write_dir + "/output5.jpg", frame)

        cv.waitKey(0)
        cv.destroyAllWindows()

    def run1(self):
        comp_path = "ref_images/fishing_space_bar.jpg"
        stream_path = "screenshots/space_img001.jpg"

        method = cv.TM_SQDIFF

        comp_img = cv.imread(comp_path, 0)
        stream_img = cv.imread(stream_path, 0)

        # cv.imshow("comp", comp_img)
        # cv.imshow("stream", stream_img)

        result = cv.matchTemplate(comp_img, stream_img, method)

        mn, _, mnLoc, _ = cv.minMaxLoc(result)
        MPx, MPy = mnLoc

        if (MPx > target_x - target_thresh and MPx < target_x + target_thresh and MPy > target_y - target_thresh and MPy < target_y + target_thresh):
            trows,tcols = comp_img.shape[:2]
            cv.rectangle(stream_img, (MPx, MPy), (MPx + tcols, MPy + trows), (0, 0, 255), 2)

        cv.imshow("output", stream_img)

        cv.waitKey(0)
        cv.destroyAllWindows()

    def hasNoBordered(img, y, x, h=-1, w=-1):
        for dy in range(-1, 2):
            if y+dy > 0 and (h < 0 or y+dy < h):
                for dx in range(-1, 2):
                    if x+dx > 0 and (w < 0 or x+dx < w):
                        if img[y + dy, x + dx] > pixel_thresh:
                            return False
        return True

    def image_combiner():
        output_folder = "ref_images"
        output_name = "combined_key_color2.tiff"
        key_output_names = ["w_key_color.tiff", "a_key_color.tiff", "s_key_color.tiff", "d_key_color.tiff"]
        input_folder = "ref_images/keys_orig/"
        imgs = [cv.imread(input_folder + "w_key_centered.jpg", 1), cv.imread(input_folder + "a_key_centered.jpg", 1), cv.imread(input_folder + "s_key_centered.jpg", 1), cv.imread(input_folder + "d_key_centered.jpg", 1)]

        thresh = 120
        added_border = 2
        amnt_to_mask = 2
        w, h = imgs[0].shape[1], imgs[0].shape[0]

        # generate normal mask
        out_img = np.zeros((h, w, 3), np.uint8)
        mask_img = np.zeros((h, w), np.uint8)
        for img in imgs:
            mask = img[:, :, 2] > thresh
            out_img[mask] = out_img[mask] + [0, 0, 50]
            mask_img[mask] = 255

        # generate inverse mask
        has_bordering = np.zeros((h, w), np.uint8)
        kernel = np.ones((3, 3), np.uint8)
        for i in range(h):
            for j in range(w):
                if Runs.hasNoBordered(mask_img, i, j, h, w):
                    out_img[i, j, 1] = 255

        # clean up normal mask
        for i in range(h):
            for j in range(w):
                v = out_img[i, j, 2]
                if v > 25:
                    if v < 125:
                        out_img[i, j, 2] = 0
                    else:
                        out_img[i, j, 2] = 255

        # shrink and add border
        out_img_bigger = np.zeros((h + added_border * 2, w + added_border * 2, 3))
        imgs_bigger = []
        for k in range(4):
            imgs_bigger.append(np.zeros((h + added_border * 2, w + added_border * 2, 3)))
        for i in range(-added_border, h + added_border):
            for j in range(-added_border, w + added_border):
                if i >= 0 and i < h and j >= 0 and j < w:
                    out_img_bigger[i + added_border, j + added_border] = out_img[i, j]
                    for k in range(4):
                        imgs_bigger[k][i + added_border, j + added_border] = imgs[k][i, j]
                else:
                    out_img_bigger[i + added_border, j + added_border] = [0, 255, 0]
                    for k in range(4):
                        imgs_bigger[k][i + added_border, j + added_border] = [0, 255, 0]

        min_x, max_x, min_y, max_y = w + 10, 0, h + 10, 0
        for yy in range(out_img_bigger.shape[0]):
            for xx in range(out_img_bigger.shape[1]):
                if out_img_bigger[yy, xx, 1] < thresh:
                    if xx > max_x:
                        max_x = xx
                    if xx < min_x:
                        min_x = xx
                    if yy > max_y:
                        max_y = yy
                    if yy < min_y:
                        min_y = yy
        print(min_y)
        print(max_y)
        cut_left, cut_right = min_x - added_border, out_img_bigger.shape[1] - max_x - added_border - 1
        cut_up, cut_down = min_y - added_border, out_img_bigger.shape[0] - max_y - added_border - 1
        print(out_img_bigger.shape)
        print(str(cut_left) + ", " + str(cut_right) + ", " + str(cut_up) + ", " + str(cut_down))

        out_img_cropped = np.zeros((out_img_bigger.shape[0] - cut_up - cut_down, out_img_bigger.shape[1] - cut_left - cut_right, 3), np.uint8)
        imgs_cropped = []
        for i in range(4):
            imgs_cropped.append(np.zeros((out_img_bigger.shape[0] - cut_up - cut_down, out_img_bigger.shape[1] - cut_left - cut_right, 3), np.uint8))
        print(out_img_cropped.shape)
        for i in range(out_img_cropped.shape[0]):
            for j in range(out_img_cropped.shape[1]):
                out_img_cropped[i, j] = out_img_bigger[i + cut_up, j + cut_left]
                for k in range(4):
                    imgs_cropped[k][i, j] = imgs_bigger[k][i + cut_up, j + cut_left]

        # write to file
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        cv.imwrite(output_folder + "/" + output_name, out_img_cropped)
        # for k in range(4):
        #     cv.imwrite(output_folder + "/" + key_output_names[k], imgs_cropped[k])

        # show if wanted
        show_source = False
        show_mask = True
        show_keys = False
        if show_source:
            c = 1
            for img in imgs:
                cv.imshow("img" + str(c), img)
                c += 1
        if show_mask:
            cv.imshow("out", out_img_cropped)
        if show_keys:
            for i in range(4):
                cv.imshow("img" + str(i), imgs_cropped[i])
        if show_source or show_mask or show_keys:
            cv.waitKey(0)
            cv.destroyAllWindows()

    def mask_creator():
        input_path = "ref_images/keys_orig/d_key_mask.jpg"
        output_folder = "ref_images"
        output_name = "d_key_color.tiff"
        thresh = 127

        added_border = 2

        show_source = True
        show_mask = True

        input = cv.imread(input_path, 0)
        rows, cols = input.shape
        min_x, max_x, min_y, max_y = rows, 0, cols, 0


        for yy in range(rows):
            for xx in range(cols):
                if input[yy, xx] > thresh:
                    if xx > max_x:
                        max_x = xx
                    if xx < min_x:
                        min_x = xx
                    if yy > max_y:
                        max_y = yy
                    if yy < min_y:
                        min_y = yy

        w, h = max_x - min_x + 1 + added_border * 2, max_y - min_y + 1 + added_border * 2
        mask = np.zeros((h, w, 3), np.uint8)

        for yy in range(mask.shape[0]):
            for xx in range(mask.shape[1]):
                if input[min_y + yy - added_border, min_x + xx - added_border] > thresh:
                    mask[yy, xx] = [0, 0, 255]
                elif Runs.hasNoBordered(input, min_y + yy - added_border, min_x + xx - added_border):
                    mask[yy, xx] = [0, 255, 0]

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        cv.imwrite(output_folder + "/" + output_name, mask)

        if show_source:
            cv.rectangle(input, (min_x, min_y), (max_x, max_y), 255, 1)
            cv.imshow("input", input)

        if show_mask:
            cv.imshow("mask", mask)

        if show_source or show_mask:
            cv.waitKey(0)
            cv.destroyAllWindows()


if __name__ == "__main__":
    Runs.run9()
