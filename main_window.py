import os, sys, random
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
    def __init__(self, appQuitPntr):
        super(MainWindow, self).__init__()
        self.appQuitPntr = appQuitPntr

        tabWidget = QTabWidget()

        self.masterTab = MasterTab()
        tabWidget.addTab(self.masterTab, "Controller")

        tabs = [
            AutoFishingTab(),
            # EnergyTab(),
            # StreamTab(),
            # FishTab(),
        ]
        for tab in tabs:
            tabWidget.addTab(tab, tab.name)
            tab.getModuleFrom(self.masterTab.controller)

        layout = QVBoxLayout()
        layout.addWidget(tabWidget)
        self.setLayout(layout)

        self.setWindowTitle("Fuzzy Waddle v1.1")

    def closeEvent(self, event):
        print('terminating thread')
        self.masterTab.controller.terminate()
        event.accept()
        # TODO: make the app close more gracefully
        os._exit(0)


def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if __name__ == "__main__":
    if is_admin():
        app = QApplication()

        mainWin = MainWindow(app.quit)
        mainWin.setFixedSize(1280, 720)
        mainWin.show()

        sys.exit(app.exec_())
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
