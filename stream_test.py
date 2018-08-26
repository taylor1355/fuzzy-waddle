import sys, time

import Utils

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QWidget, QPushButton, QLabel
from PySide2.QtGui import QPixmap

class StreamTab(QWidget):
    def __init__(self):
        super(StreamTab, self).__init__()
        openStreamButton = Utils.createButton("Open Stream", self)
        openStreamButton.released.connect(self._open_stream)

    def _open_stream(self):
        self.streamWindow = StreamWindow()
        self.streamWindow.show()


class StreamWindow(QWidget):
    def __init__(self):
        super(StreamWindow, self).__init__()
        w, h = 1280, 720
        self.setFixedSize(w, h)
        self.setWindowTitle("Streaming Test")
        self.imageLabel = QLabel(self)
        self.imageLabel.setGeometry(0, 0, w, h)

        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self._update_timer_tick);
        self.updateTimer.start()

    def setImage(self, pixmap):
        self.imageLabel.setPixmap(pixmap)

    def _update_timer_tick(self):
        # update code here
        print("in the updater")
        time.sleep(1)
