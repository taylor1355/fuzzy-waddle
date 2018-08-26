import sys

from PySide2.QtWidgets import QApplication, QLabel, QPushButton, QMainWindow, QWidget

class HomeTab(QWidget):
    def __init__(self):
        super(HomeTab, self).__init__()

        button1 = QPushButton("Test Button", self)
        button1.released.connect(self._button_cb)

    def _button_cb(self):
        print("Home Tab Button!!!")
