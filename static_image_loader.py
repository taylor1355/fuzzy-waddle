import os, sys, time
import pyautogui
import cv2 as cv
import numpy as np

comp_path = "ref_images/fishing_space_bar.jpg"
stream_path = "screenshots/space_img001.jpg"

target_x = 574
target_y = 240
target_thresh = 3

if __name__ == "__main__":
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
