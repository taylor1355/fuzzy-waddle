import os, sys, time
import numpy as np
import cv2 as cv

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from utils.game_window import GameWindow
from utils.ui_generator import *

class AutoFishingTab(QWidget):
    name = "Auto Fishing"
    def __init__(self):
        super(AutoFishingTab, self).__init__()
        self.isEnabledCheckBox = createCheckBox("Enabled", self, 0, 0)
        self.isEnabledCheckBox.stateChanged.connect(self._is_enabled_checkbox_changed)
        self.outputColorsCheckBox = createCheckBox("Output Colors", self, 0, 1)
        self.outputColorsCheckBox.stateChanged.connect(self._output_colors_checkbox_changed)
        self.outputKeysCheckBox = createCheckBox("Output Keys", self, 0, 2)
        self.outputKeysCheckBox.stateChanged.connect(self._output_keys_checkbox_changed)

        self.collectAllCheckBox = createCheckBox("Collect All", self, 1, 0, Qt.Checked)
        self.collectAllCheckBox.stateChanged.connect(self._collect_all_checkbox_changed)

        self.discardBlueCheckBox = createCheckBox("Discard Blue", self, 1, 1)
        self.discardBlueCheckBox.stateChanged.connect(self._discard_blue_checkbox_changed)
        self.discardGreenCheckBox = createCheckBox("Discard Green", self, 1, 2)
        self.discardGreenCheckBox.stateChanged.connect(self._discard_green_checkbox_changed)
        self.collectUnknownsCheckBox = createCheckBox("Collect Other", self, 1, 3)
        self.collectUnknownsCheckBox.stateChanged.connect(self._collect_unknowns_checkbox_changed)
        self.setCollectAll(True)

        self.swapRodsCheckBox = createCheckBox("Swap Rods", self, 2, 0)
        self.swapRodsCheckBox.stateChanged.connect(self._swap_rods_checkbox_changed)
        self.rodCharSeqTextBox = createTextBox(self, 2, 1)
        self.setRodSeqButton = createButton("Set Rod Seq", self, 2, 2)
        self.setRodSeqButton.released.connect(self._set_rod_seq_button_handler)
        self.setSwapRods(False)

    def getModuleFrom(self, controller):
        self.autoFishingModule = controller.autoFishingModule

    def setSwapRods(self, swapRods):
        self.rodCharSeqTextBox.setEnabled(swapRods)
        self.setRodSeqButton.setEnabled(swapRods)

    def setCollectAll(self, collectAll):
        self.discardBlueCheckBox.setEnabled(not collectAll)
        self.discardGreenCheckBox.setEnabled(not collectAll)
        self.collectUnknownsCheckBox.setEnabled(not collectAll)

    def _is_enabled_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled auto fishing")
            self.autoFishingModule.isEnabled = True
            # self.setEnabled(True)
        else:
            print("disabled auto fishing")
            self.autoFishingModule.isEnabled = False
            # self.setEnabled(False)

    def _output_colors_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled output color data")
            self.autoFishingModule.outputColors = True
        else:
            print("disabled output color data")
            self.autoFishingModule.outputColors = False

    def _output_keys_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled output keys data")
            self.autoFishingModule.outputKeys = True
        else:
            print("disabled output keys data")
            self.autoFishingModule.outputKeys = False

    def _collect_all_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled collect all")
            self.autoFishingModule.collectAll = True
        else:
            print("disabled collect all")
            self.autoFishingModule.collectAll = False
        self.setCollectAll(self.autoFishingModule.collectAll)

    def _discard_blue_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled discard blue")
            self.autoFishingModule.discardBlue = True
            self.autoFishingModule.discardGreen = True
            self.discardGreenCheckBox.setCheckState(Qt.Checked)
        else:
            print("disabled discard blue")
            self.autoFishingModule.discardBlue = False

    def _discard_green_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled discard green")
            self.autoFishingModule.discardGreen = True
        else:
            print("disabled discard green")
            self.autoFishingModule.discardGreen = False
            self.autoFishingModule.discardBlue = False
            self.discardBlueCheckBox.setCheckState(Qt.Unchecked)

    def _collect_unknowns_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled collect unknowns")
            self.autoFishingModule.collectUnknowns = True
        else:
            print("disabled collect unknowns")
            self.autoFishingModule.collectUnknowns = False

    def _swap_rods_checkbox_changed(self, state):
        if state == Qt.Checked:
            print("enabled swapping rods")
            self.autoFishingModule.swapRods = True
        else:
            print("disabled swapping rods")
            self.autoFishingModule.swapRods = False
        self.setSwapRods(self.autoFishingModule.swapRods)

    def _set_rod_seq_button_handler(self):
        self.autoFishingModule.rodCharSeq = self.rodCharSeqTextBox.text()
        print(f"set rod charcter sequence to '{self.autoFishingModule.rodCharSeq}'")

