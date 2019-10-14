import sys

from utils.ui_generator import *

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

item_width = 80
item_height = 80
gap_width = 4
gap_height = 4

class Numpad(QWidget):
    def __init__(self, type):
        super(Numpad, self).__init__()
        self.type = type
        self.mapper = QSignalMapper(self)
        # if type == 0:
        #     text = "0"
        # else:
        text = "0:00"
        self.outputLabel = createLabel(text, self, 0, 0)
        x, y, w, h = gap_width, gap_height, item_width * 4 + gap_width * 3, item_height
        self.outputLabel.setGeometry(x, y, w, h)
        for x in range(3):
            for y in range(3):
                self.createButton(str(x*3+y+1), x, y+1, x*3+y+1)
        self.createButton("<-", 3, 1, -1)
        self.createButton("Clear", 3, 2, -2)
        self.createButton("Cancel", 3, 3, -3)
        self.createButton("Enter", 3, 4, -4)
        b = self.createButton("0", 0, 4, 0)
        x, y = gap_width, gap_height + (4 * (gap_height + item_height))
        b.setGeometry(x, y, item_width * 3 + gap_width * 2, item_height)

        self.connect(self.mapper, SIGNAL("mapped(int)"), self._int_mapped)

        x, y = item_width * 4 + gap_width * 5, item_height * 5 + gap_height * 6
        self.setFixedSize(x, y)
        self.setWindowTitle("Numpad")

    def _int_mapped(self, value):
        if value >= 0:
            # number
            self.amnt = self.amnt * 10 + value
        elif value == -1:
            # backspace
            self.amnt /= 10
        elif value == -2:
            # clear
            self.amnt = 0
        elif value == -3:
            # cancel
            self.reset()
            self.hide()
        elif value == -4:
            # enter
            self.emit(SIGNAL("send_int(int)"), self.amnt)
            self.reset()
            self.hide()

        # update the label
        if self.type == 0:
            self.outputLabel.setText(str(self.amnt))
        else:
            self.outputLabel.setText("%d" % int(self.amnt / 100) + ":" + "%02.0d" % int(self.amnt % 100))

    def reset(self):
        self.amnt = 0
        if self.type == 0:
            self.outputLabel.setText("0")
        elif type == 1:
            self.outputLabel.setText("0:00")


    def createButton(self, text, x, y, id):
        button = createButton(text, self, 0, 0)
        x, y = gap_width + (x * (gap_width + item_width)), gap_height + (y * (gap_height + item_height))
        button.setGeometry(x, y, item_width, item_height)
        self.connect(button, SIGNAL("released()"), self.mapper, SLOT("map()"))
        self.mapper.setMapping(button, id)
        return button
