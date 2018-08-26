import sys

from PySide2.QtWidgets import QPushButton

def createButton(text, parent):
    button = QPushButton(text, parent)
    x, y, w, h = 10, 10, 120, 56
    button.setGeometry(x, y, w, h)
    return button
