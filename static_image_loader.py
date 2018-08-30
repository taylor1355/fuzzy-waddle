import os, sys, time
import pyautogui
import cv2 as cv
import numpy as np


target_x = 574
target_y = 240
target_thresh = 3
pixel_thresh = 127

class Runs():

    def getStdDev(window, mask, x, y):
        total, cntr = [0, 0, 0], 1
        h, w = mask.shape

        for yy in range(h):
            for xx in range(w):
                if mask[yy, xx] > pixel_thresh:
                    total += window[y + yy, x + xx]
                    cntr += 1

        avg = total / cntr
        dev_sq_total = [0, 0, 0]

        for yy in range(h):
            for xx in range(w):
                if mask[yy, xx] > pixel_thresh:
                    dev_sq_total += np.square(avg - window[y + yy, x + xx])

        std_dev = np.sqrt(dev_sq_total / cntr)
        avg_std_dev = (std_dev[0] + std_dev[1] + std_dev[2]) / 3
        return avg_std_dev

    def run3():
        mask_path = "ref_images/w_key.jpg"
        window_path = "screenshots/keys_img001.jpg"

        mask = cv.imread(mask_path, 0)
        window = cv.imread(window_path, 1)

        # x, y, w, h = 465, 395, 30, 32
        x, y, dx, dy, w, h = 463, 380, 30, 30, mask.shape[1], mask.shape[0]

        min, min_x, min_y = 50, 0, 0
        for dyy in range(dy):
            for dxx in range(dx):
                val = Runs.getStdDev(window, mask, x + dxx, y + dyy)
                if (val < min):
                    min = val
                    min_x = dxx
                    min_y = dyy

        print(min)

        for yy in range(h):
            for xx in range(w):
                if mask[yy, xx] > pixel_thresh:
                    window[y + yy + min_y, x + xx + min_x] = [255, 0, 0]

        cv.rectangle(window, (x, y), (x + w + dx, y + h + dy), (0, 0, 255), 2)
        cv.imshow("output", window)

        cv.waitKey(0)
        cv.destroyAllWindows()







    def run2():
        mask_path = "screenshots/w_key_po1.jpg"
        stream_path = "screenshots/keys_img001.jpg"
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

    def mask_creator():
        input_path = "screenshots/w_key_po1.jpg"
        output_folder = "ref_images"
        output_name = "w_key.jpg"
        thresh = 127

        show_source = False
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

        w, h = max_x - min_x + 1, max_y - min_y + 1
        mask = np.zeros((h, w, 3), np.uint8)

        for yy in range(mask.shape[0]):
            for xx in range(mask.shape[1]):
                if input[min_y + yy, min_x + xx] > thresh:
                    mask[yy, xx] = input[min_y + yy, min_x + xx]

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
    Runs.run3()
