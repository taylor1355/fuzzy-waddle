import sys, time

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from utils.ui_generator import *
from utils.numpad import Numpad

class EnergyTab(QWidget):
    name = "Energy"
    def __init__(self):
        super(EnergyTab, self).__init__()

        self.startTime = time.time()

        self.timeLabel = createLabel("3:00", self, 0, 0)
        self.startTimerButton = createButton("Start", self, 1, 0)
        self.startTimerButton.released.connect(self._start_timer)
        self.resetTimerButton = createButton("Reset", self, 2, 0)
        self.resetTimerButton.released.connect(self._reset_time)

        self.soundItem1 = SoundItem(self, 2)

        self.isTimerOn = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._timer_tick)

    def getModuleFrom(self, controller):
        pass

    def _start_timer(self):
        if self.isTimerOn == True:
            self.timer.stop()
            self.startTimerButton.setText("Start")
            self.timeLabel.setText("3:00")
            self.isTimerOn = False;
        else:
            self.startTime = time.time()
            self.timer.start()
            self.startTimerButton.setText("Stop")
            self.isTimerOn = True;

    def _reset_time(self):
        self.startTime = time.time()
        self.timeLabel.setText("3:00")

    def _timer_tick(self):
        now = time.time()
        diff = int(180 - (now - self.startTime))
        if (now > self.startTime + 180):
            self.startTime += 180
        seconds = int(diff % 60)
        minutes = int(diff / 60)
        self.timeLabel.setText("%d" % int(minutes) + ":" + "%02.0d" % int(seconds))






class SoundItem():
    def __init__(self, parent, y):
        self.soundCheckBox = createCheckBox("Enabled", parent, 0, y)
        self.soundCheckBox.stateChanged.connect(self._sound_checkbox_changed)
        self.isSoundEnabled = False
        self.soundLabel = createLabel("0:00", parent, 1, y)
        self.timeToSound = 0
        self.editTimeButton = createButton("Edit Time", parent, 2, y)
        self.editTimeButton.released.connect(self._edit_time_button_handler)
        self.numpad = Numpad(1)
        # self.connect(self.numpad, SIGNAL("send_int(int)"), self._receive_numpad_int)

    def _sound_checkbox_changed(self, state):
        if state == Qt.Checked:
            self.isSound1Enabled = True
        else:
            self.isSound1Enabled = False

    def _edit_time_button_handler(self):
        self.numpad.reset()
        self.numpad.show()

    def _receive_numpad_int(self, value):
        self.timeToSound = value
        seconds = value % 100
        minutes = val;ue / 100
        if seconds >= 60:
            seconds -= 60
            minutes += 1
        self.soundLabel.setText("%d" % int(minutes) + ":" + "%02.0d" % int(seconds))













# a
