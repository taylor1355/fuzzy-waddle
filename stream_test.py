import sys, time

import utils

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class StreamTab(QWidget):
    def __init__(self):
        super(StreamTab, self).__init__()
        openStreamButton = utils.createButton("Open Stream", self, 0, 0)
        openStreamButton.released.connect(self._open_stream)
        closeStreamButton = utils.createButton("Close Stream", self, 0, 1)
        closeStreamButton.released.connect(self._close_stream)

        startWorkerButton = utils.createButton("Start Worker", self, 0, 2)
        startWorkerButton.released.connect(self._start_worker)
        stopWorkerButton = utils.createButton("Stop Worker", self, 0, 3)
        stopWorkerButton.released.connect(self._stop_worker)

        self.streamWindow = StreamWindow()
        self.isWindowShown = False;
        self.thread = StreamThread()

        self.workerLabel = utils.createLabel("", self, 0, 4)
        self.connect(self.thread, SIGNAL("send_back_qstring(QString)"), self._get_qstring)

    def _get_qstring(self, text):
        self.workerLabel.setText(text)
        if self.isWindowShown == True:
            self.streamWindow.setText(text + " has been passed through")

    def _open_stream(self):
        self.isWindowShown = True;
        self.streamWindow.show()

    def _close_stream(self):
        self.isWindowShown = False;
        self.streamWindow.hide()

    def _start_worker(self):
        self.thread.start()

    def _stop_worker(self):
        self.thread.terminate()


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
        while 1:
            self.emit(SIGNAL("send_back_qstring(QString)"), "this is some text")
            time.sleep(1)
            self.emit(SIGNAL("send_back_qstring(QString)"), "this is some other text")
            time.sleep(1)
