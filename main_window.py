import sys
import ctypes

import utils
from home import HomeTab
from energy import EnergyTab
from stream_test import StreamTab

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()

        tabWidget = QTabWidget()

        homeTab = HomeTab()
        tabWidget.addTab(homeTab, "Home")
        energyTab = EnergyTab()
        tabWidget.addTab(energyTab, "Energy")
        streamTab = StreamTab()
        tabWidget.addTab(streamTab, "Stream Test")

        layout = QVBoxLayout()
        layout.addWidget(tabWidget)
        self.setLayout(layout)

        self.setWindowTitle("Fuzzy Waddle v1.0")

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if __name__ == "__main__":
    if is_admin():
        app = QApplication()

        mainWin = MainWindow()
        x, y = 1280, 720
        mainWin.setFixedSize(x, y)
        mainWin.show()

        sys.exit(app.exec_())
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
