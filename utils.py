import sys

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

font = QFont()
font.setPointSize(14)
font.setBold(False)

origin_x = 32
origin_y = 32
gap_width = 8
gap_height = 8
item_width = 160
item_height = 64

def createButton(text, parent):
    button = QPushButton(text, parent)
    button.setGeometry(gap_width, gap_height, item_width, item_height)
    button.setFont(font)
    return button

def createButton(text, parent, x, y):
    button = QPushButton(text, parent)
    x, y = origin_x + (x * (item_width + gap_width)), origin_y + (y * (item_height + gap_height))
    button.setGeometry(x, y, item_width, item_height)
    button.setFont(font)
    return button

def createLabel(text, parent, x, y):
    label = QLabel(text, parent)
    x, y = origin_x + (x * (item_width + gap_width)), origin_y + (y * (item_height + gap_height))
    label.setGeometry(x, y, item_width, item_height)
    label.setFont(font)
    label.setAlignment(Qt.AlignCenter)
    return label

# def createLabelCText(text, parent, x, y):
#     label = createLabel(text, parent, x, y)
#     label.setAlignment(Qt.AlignCenter)
#     return label

def createCheckBox(text, parent, x, y):
    checkBox = QCheckBox(text, parent)
    x, y = origin_x + (x * (item_width + gap_width)), origin_y + (y * (item_height + gap_height))
    checkBox.setGeometry(x, y, item_width, item_height)
    checkBox.setFont(font)
    checkBox.setStyleSheet("margin-left:30%; margin-right:0%;")
    return checkBox
