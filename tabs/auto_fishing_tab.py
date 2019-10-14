import os, sys, time

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from utils.ui_generator import *

class AutoFishingTab(QWidget):
    def __init__(self):
        super(AutoFishingTab, self).__init__()
        self.isEnabledCheckBox = createCheckBox("Enabled", self, 0, 0)
        self.isEnabledCheckBox.stateChanged.connect(self._is_enabled_checkbox_changed)

        self.outputCheckBox = createCheckBox("Output", self, 0, 1)
        self.outputCheckBox.setEnabled(False)
        self.outputCheckBox.stateChanged.connect(self._output_checkbox_changed)

    def _is_enabled_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled auto fishing")
            self.autoFishingModule.isEnabled = True
            self.setEnabled(True)
        else:
            print("disabled auto fishing")
            self.autoFishingModule.isEnabled = False
            self.setEnabled(False)

    def setEnabled(self, enabled):
        self.outputCheckBox.setEnabled(enabled)

    def _output_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled output training data")
            self.autoFishingModule.keySequenceDetector.output = True
        else:
            print("disabled output training data")
            self.autoFishingModule.keySequenceDetector.output = False

