import os, sys, time, uuid
import pyautogui
import cv2 as cv

from game_window import GameWindow
import direct_input
import input
import utils
from static_image_loader import KeyDetector

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class StreamTab(QWidget):
    def __init__(self):
        super(StreamTab, self).__init__()
        openStreamButton = utils.createButton("Open Stream", self, 0, 0)
        openStreamButton.released.connect(self._open_stream_button_handler)
        closeStreamButton = utils.createButton("Close Stream", self, 0, 1)
        closeStreamButton.released.connect(self._close_stream_button_handler)

        startWorkerButton = utils.createButton("Start Worker", self, 0, 2)
        startWorkerButton.released.connect(self._start_worker_button_handler)
        stopWorkerButton = utils.createButton("Stop Worker", self, 0, 3)
        stopWorkerButton.released.connect(self._stop_worker_button_handler)

        takeScreenshotButton = utils.createButton("Take Screenshot", self, 0, 5)
        takeScreenshotButton.released.connect(self._take_screenshot_button_handler)

        charDetectionButton = utils.createButton("Detect Char", self, 0, 6)
        charDetectionButton.released.connect(self._char_detection_button_handler)
        stopCharDetectionButton = utils.createButton("Stop Detect Char", self, 0, 7)
        stopCharDetectionButton.released.connect(self._stop_char_detection_button_handler)

        self.streamWindow = StreamWindow()
        self.isWindowShown = False;
        self.thread = StreamThread()
        self.screeshotThread = ScreenshotThread()
        self.charDetectionThread = CharacterDetectionThread()

        self.workerLabel = utils.createLabel("Worker is Sleeping", self, 0, 4)
        self.connect(self.thread, SIGNAL("send_back_qstring(QString)"), self._get_qstring)

    def _get_qstring(self, text):
        self.workerLabel.setText(text)
        if self.isWindowShown == True:
            self.streamWindow.setText(text + " has been passed through")

    def _open_stream_button_handler(self):
        self.isWindowShown = True;
        self.streamWindow.show()

    def _close_stream_button_handler(self):
        self.isWindowShown = False;
        self.streamWindow.hide()

    def _start_worker_button_handler(self):
        self.thread.start()
        self.workerLabel.setText("Worker is Running")

    def _stop_worker_button_handler(self):
        self.thread.terminate()
        self.workerLabel.setText("Worker is Sleeping")

    def _take_screenshot_button_handler(self):
        self.screeshotThread.start()

    def _char_detection_button_handler(self):
        self.charDetectionThread.start()

    def _stop_char_detection_button_handler(self):
        self.charDetectionThread.terminate()


class StreamWindow(QWidget):
    def __init__(self):
        super(StreamWindow, self).__init__()
        w, h = 1280, 720
        self.setFixedSize(w, h)
        self.setWindowTitle("Streaming Test")
        self.imageLabel = QLabel(self)
        self.imageLabel.setGeometry(0, 0, w, h)

    def setImage(self, pixmap):
        self.imageLabel.setPixmap(pixmap)

    def setText(self, text):
        self.imageLabel.setText(text)



class StreamThread(QThread):
    def __init__(self):
        super(StreamThread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()

        point = window.rect.center()
        pyautogui.moveTo(point[0], point[1], duration=2)

        while 1:
            direct_input.PressKey("R")
            time.sleep(1)
            direct_input.ReleaseKey("R")
            time.sleep(1)



class ScreenshotThread(QThread):
    def __init__(self):
        super(ScreenshotThread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()

        # take screenshot here
        print("taking screenshot")
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        file_name = str(uuid.uuid4()) + ".jpg"
        cv.imwrite(os.path.join(screenshot_dir, file_name), window.grab_frame())

pixel_thresh = 140

class CharacterDetectionThread(QThread):
    def __init__(self):
        super(CharacterDetectionThread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()

        print("grabbing")

        w_mask_path = "ref_images/w_key_color.jpg"
        a_mask_path = "ref_images/w_key_color.jpg"
        s_mask_path = "ref_images/w_key_color.jpg"
        d_mask_path = "ref_images/w_key_color.jpg"
        # window_path = "screenshots/keys_img004.jpg"

        w_mask = cv.imread(w_mask_path, 1)
        a_mask = cv.imread(a_mask_path, 1)
        s_mask = cv.imread(s_mask_path, 1)
        d_mask = cv.imread(d_mask_path, 1)
        # frame = cv.imread(window_path, 0)
        # color_frame = cv.imread(window_path)
        color_frame = window.grab_frame()
        frame = cv.cvtColor(color_frame, cv.COLOR_BGR2GRAY)

        w_key_detector = KeyDetector(w_mask, 0)
        a_key_detector = KeyDetector(a_mask, 0)
        s_key_detector = KeyDetector(s_mask, 0)
        d_key_detector = KeyDetector(d_mask, 0)
        for i in range(1):
            w_key_detector.processFrame(frame)
            a_key_detector.processFrame(frame)
            s_key_detector.processFrame(frame)
            d_key_detector.processFrame(frame)
        # if w_key_detector.cntr == 0:
        #     print("Error: no images processed")
        #     return

        w_max, _, _ = w_key_detector.getMaxAndPos()
        a_max, _, _ = a_key_detector.getMaxAndPos()
        s_max, _, _ = s_key_detector.getMaxAndPos()
        d_max, _, _ = d_key_detector.getMaxAndPos()

        max_x, max_y = 0, 0
        if w_max > a_max and w_max > s_max and w_max > d_max:
            _, max_x, max_y = w_key_detector.getMaxAndPos()
            mask = w_mask
        elif a_max > s_max and a_max > d_max:
            _, max_x, max_y = a_key_detector.getMaxAndPos()
            mask = a_mask
        elif s_max > d_max:
            _, max_x, max_y = s_key_detector.getMaxAndPos()
            mask = s_mask
        else:
            _, max_x, max_y = d_key_detector.getMaxAndPos()
            mask = d_mask

        mask_red = mask[:, :, 2] > pixel_thresh
        h, w = mask.shape[0], mask.shape[1]
        for i in range(h):
            for j in range(w):
                if mask_red[i, j] > 0:
                    frame[w_key_detector.y + i + max_y, w_key_detector.x + j + max_x] = 255
        # cv.rectangle(color_frame, (w_key_detector.x, w_key_detector.y), (w_key_detector.x + w + w_key_detector.dx, w_key_detector.y + h + w_key_detector.dy), (255, 0, 0), 2)

        print("finished grabbing")
        cv.imshow("frame", frame)
        cv.waitKey(0)
        cv.destroyAllWindows()
