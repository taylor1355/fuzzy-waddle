import numpy as np
import cv2 as cv
import pyautogui
import time

def main():
    time.sleep(3)

    pyautogui.moveTo(500, 500, duration=2, tween=pyautogui.easeInOutQuad)  # use tweening/easing function to move mouse over 2 seconds.
    cv.waitKey(0)

if __name__ == "__main__":
    main()
