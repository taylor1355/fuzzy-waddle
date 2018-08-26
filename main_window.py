import sys

import Utils
from Home import HomeTab
from StreamTest import StreamTab

from PySide2.QtWidgets import QApplication, QLabel, QPushButton, QMainWindow, QDialog, QTabWidget, QWidget, QVBoxLayout

class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()

        tabWidget = QTabWidget()

        homeTab = HomeTab()
        tabWidget.addTab(homeTab, "Home")
        streamTab = StreamTab()
        tabWidget.addTab(streamTab, "Stream Test")

        layout = QVBoxLayout()
        layout.addWidget(tabWidget)
        self.setLayout(layout)

        self.setWindowTitle("Window Test v1.0")

if __name__ == "__main__":
    app = QApplication()

    mainWin = MainWindow()
    x, y = 1280, 720
    mainWin.setFixedSize(x, y)
    mainWin.show()

    sys.exit(app.exec_())
