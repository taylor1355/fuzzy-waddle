import os, sys, time
import pyautogui
import cv2 as cv
import numpy as np


target_x = 574
target_y = 240
target_thresh = 3
pixel_thresh = 160

class Runs():

    def run5():
        a = [[1, 2, 3, 4], [4, 5, 6, 7], [7, 8, 9, 10], [10, 11, 12, 13]]
        b = [[2, 2], [2, 2]]
        npa = np.array(a)
        npb = np.array(b)
        i = 1;
        n = 2;
        npc = np.zeros((3, 3), np.uint8)
        for yy in range(3):
            for xx in range(3):
                npc[yy, xx] = np.sum(npa[yy:yy+2, xx:xx+2]*npb[:, :])
        print(npc)

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

    def hasNoBordered(img, y, x):
        for yy in range(-1, 2):
            for xx in range(-1, 2):
                if img[y + yy, x + xx] > pixel_thresh:
                    return False
        return True

    def mask_creator():
        input_path = "screenshots/w_key2.jpg"
        output_folder = "ref_images"
        output_name = "w_key_color2.jpg"
        thresh = 127

        added_border = 2

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
    Runs.run4()
