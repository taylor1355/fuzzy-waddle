import sys, time
import pyautogui

from game_window import GameWindow
import direct_input
import input

import utils

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

        self.streamWindow = StreamWindow()
        self.isWindowShown = False;
        self.thread = StreamThread()

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
