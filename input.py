from game_window import GameWindow
import direct_input
import numpy as np
import cv2 as cv
import pyautogui
import time
import ctypes
import sys

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def main():
    window = GameWindow("BLACK DESERT")
    window.move_to_foreground()

    point = window.local_to_global((720, 360))
    pyautogui.moveTo(point[0], point[1], duration=2)
    time.sleep(2)

    pyautogui.mouseDown(button='right')
    time.sleep(2)
    pyautogui.mouseUp(button='right')

    direct_input.PressKey("R")
    time.sleep(1)
    direct_input.ReleaseKey("R")

    time.sleep(12)

    direct_input.PressKey("R")
    time.sleep(1)
    direct_input.ReleaseKey("R")

    while True:
        cv.imshow("Window", window.grab_frame())
        if cv.waitKey(1) == ord('q'):
            break

if __name__ == "__main__":
    if is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
