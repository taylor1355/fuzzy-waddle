import sys

from PySide2.QtWidgets import QPushButton, QLabel

def createButton(text, parent):
    button = QPushButton(text, parent)
    x, y, w, h = 10, 10, 120, 56
    button.setGeometry(x, y, w, h)
    return button

def createButton(text, parent, x, y):
    button = QPushButton(text, parent)
    x, y, w, h = 10 + (x * 130), 10 + (y * 66), 120, 56
    button.setGeometry(x, y, w, h)
    return button

def createLabel(text, parent, x, y):
    label = QLabel(text, parent)
    x, y, w, h = 10 + (x * 130), 10 + (y * 66), 120, 56
    label.setGeometry(x, y, w, h)
    return label
