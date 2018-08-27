import sys, time

import utils

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class EnergyTab(QWidget):
    def __init__(self):
        super(EnergyTab, self).__init__()

        self.startTime = time.time()

        self.timeLabel = utils.createLabelCText("3:00", self, 0, 0)
        self.startTimerButton = utils.createButton("Start", self, 1, 0)
        self.startTimerButton.released.connect(self._start_timer)
        self.resetTimerButton = utils.createButton("Reset", self, 2, 0)
        self.resetTimerButton.released.connect(self._reset_time)

        self.isTimerOn = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._timer_tick)

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
