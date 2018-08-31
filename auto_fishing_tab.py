import os, sys, time
import utils

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class AutoFishingTab(QWidget):
    def __init__(self):
        super(AutoFishingTab, self).__init__()
        self.isEnabled = utils.createCheckBox("Enabled", self, 0, 0)
        self.isEnabled.stateChanged.connect(self._is_enabled_checkbox_changed)

    def _is_enabled_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enable auto fishing")
        else:
            print("disable auto fishing")
