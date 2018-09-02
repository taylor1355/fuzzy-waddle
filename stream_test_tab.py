import os, sys, time, uuid
import pyautogui
import cv2 as cv
import numpy as np

from game_window import GameWindow
import direct_input
import input
import utils
from static_image_loader import KeyDetectorDiff

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

        charDetectionButton = utils.createButton("Detect Char", self, 2, 0)
        charDetectionButton.released.connect(self._char_detection_button_handler)
        showImageCheckBox = utils.createCheckBox("Show Image", self, 2, 1)
        showImageCheckBox.stateChanged.connect(self._show_image_check_box_handler)
        showBorderCheckBox = utils.createCheckBox("Show Border", self, 2, 2)
        showBorderCheckBox.stateChanged.connect(self._show_border_check_box_handler)
        showOverlayCheckBox = utils.createCheckBox("Show Overlay", self, 2, 3)
        showOverlayCheckBox.stateChanged.connect(self._show_overlay_check_box_handler)


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
        self.charDetectionThread.terminate()
        self.charDetectionThread.start()

    def getBoolFromState(self, state):
        if state == Qt.Checked:
            return True
        else:
            return False

    def _show_image_check_box_handler(self, state):
        self.charDetectionThread.show_image = self.getBoolFromState(state)

    def _show_border_check_box_handler(self, state):
        self.charDetectionThread.show_border = self.getBoolFromState(state)

    def _show_overlay_check_box_handler(self, state):
        self.charDetectionThread.show_overlay = self.getBoolFromState(state)


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
        self.show_image = False
        self.show_border = False
        self.show_overlay = False

    def __del__(self):
        self.wait()

    def run(self):
        window = GameWindow("BLACK DESERT")
        window.move_to_foreground()

        print("grabbing")

        mask_path = "ref_images/combined_key_color.tiff"
        mask = cv.imread(mask_path, 1)

        output = True
        output_amnt = 5
        output_folder = "ml/keys/data/"

        positions = 2
        screenshots = 3

        show_amnt = 5

        key_detectors = []
        for i in range(positions):
            key_detectors.append(KeyDetectorDiff(mask, i))

        for f in range(screenshots):
            print(f)
            color_frame = window.grab_frame()
            frame = cv.cvtColor(color_frame, cv.COLOR_BGR2GRAY)
            for key_detector in key_detectors:
                key_detector.processFrame(frame)

        comb_frame = np.zeros((KeyDetectorDiff.dy, KeyDetectorDiff.dx), np.int16)
        for key_detector in key_detectors:
            comb_frame += key_detector.getDifferenceImage()

        if output:
            di = KeyDetectorDiff.di
            max, max_x, max_y = KeyDetectorDiff.getMaxAndPos(comb_frame)
            mask_red = mask[:, :, 2] > pixel_thresh
            h, w = mask.shape[0], mask.shape[1]
            for c in range(output_amnt):
                out_file = np.zeros((h, w, 3), np.uint8)
                out_file[:, :] = color_frame[key_detectors[0].y+max_y:key_detectors[0].y+max_y+h, key_detectors[0].x+max_x+(c * di):key_detectors[0].x+max_x+(c * di)+w]
                print("writing to file")
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                file_name = str(uuid.uuid4()) + ".jpg"
                cv.imwrite(os.path.join(output_folder, file_name), out_file)
            out_file = np.zeros((key_detectors[0].h+key_detectors[0].dy, key_detectors[0].w+key_detectors[0].dx, 3), np.uint8)
            out_file[:, :] = color_frame[key_detectors[0].y:key_detectors[0].y+h+key_detectors[0].dy, key_detectors[0].x:key_detectors[0].x+w+key_detectors[0].dx]
            if True:
                for i in range(h):
                    for j in range(w):
                        if self.show_overlay and mask_red[i, j] > 0:
                            out_file[i + max_y, j + max_x] = [255, 0, 0]
                        if self.show_border and (i < 2 or i >= h-2 or j < 2 or j >= w-2):
                            out_file[i + max_y, j + max_x] = [0, 0, 255]
            print("writing to file")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            file_name = str(uuid.uuid4()) + ".jpg"
            cv.imwrite(os.path.join(output_folder, file_name), out_file)

        if self.show_image:
            di = KeyDetectorDiff.di
            max, max_x, max_y = KeyDetectorDiff.getMaxAndPos(comb_frame)
            mask_red = mask[:, :, 2] > pixel_thresh
            h, w = mask.shape[0], mask.shape[1]
            for c in range(show_amnt):
                for i in range(h):
                    for j in range(w):
                        if self.show_overlay and mask_red[i, j] > 0:
                            color_frame[key_detectors[0].y + i + max_y, key_detectors[0].x + j + max_x + (c * di)] = [255, 0, 0]
                        if self.show_border and (i < 2 or i >= h-2 or j < 2 or j >= w-2):
                            color_frame[key_detectors[0].y + i + max_y, key_detectors[0].x + j + max_x + 35 * c] = [0, 0, 255]
                # cv.rectangle(color_frame, (key_detectors[0].x + max_x + (c*35), key_detectors[0].y + max_y), (key_detectors[0].x + w + max_x + (c*35), key_detectors[0].y + h + max_y), (0, 0, 255), 2)
            cv.imshow("frame", color_frame)
            cv.waitKey(0)
            cv.destroyAllWindows()
