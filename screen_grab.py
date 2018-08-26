import numpy as np
import cv2 as cv
import pyautogui
import mss
import time

def main():
    with mss.mss() as sct:
        # Part of the screen to capture
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

        while "Screen capturing":
            last_time = time.time()

            # Get raw pixels from the screen, save it to a Numpy array
            img = np.array(sct.grab(monitor))

            # Display the picture
            cv.imshow("OpenCV/Numpy normal", img)

            print("fps: {0}".format(1 / (time.time() - last_time)))

            # Press "q" to quit
            if cv.waitKey(25) & 0xFF == ord("q"):
                cv.destroyAllWindows()
                break

if __name__ == "__main__":
    main()
