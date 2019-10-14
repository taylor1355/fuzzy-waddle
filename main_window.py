import sys, random
import ctypes

import utils

from tabs.master_tab import MasterTab
from tabs.energy_tab import EnergyTab
from tabs.stream_test_tab import StreamTab
from tabs.auto_fishing_tab import AutoFishingTab
from tabs.fish_training_tab import FishTab

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()

        tabWidget = QTabWidget()

        masterTab = MasterTab()
        tabWidget.addTab(masterTab, "Controller")

        autoFishingTab = AutoFishingTab()
        tabWidget.addTab(autoFishingTab, "Auto Fish")
        autoFishingTab.autoFishingModule = masterTab.controller.autoFishingModule

        energyTab = EnergyTab()
        tabWidget.addTab(energyTab, "Energy")

        streamTab = StreamTab()
        tabWidget.addTab(streamTab, "Stream Test")

        fishTab = FishTab()
        tabWidget.addTab(fishTab, "Fish Data")

        layout = QVBoxLayout()
        layout.addWidget(tabWidget)
        self.setLayout(layout)

        self.setWindowTitle("Fuzzy Waddle v1.0")


def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if __name__ == "__main__":
    # if is_admin():
    app = QApplication()

    mainWin = MainWindow()
    x, y = 1280, 720
    mainWin.setFixedSize(x, y)
    mainWin.show()

    sys.exit(app.exec_())
    # else:
    #     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
