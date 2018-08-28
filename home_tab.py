import sys

import utils

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class HomeTab(QWidget):
    def __init__(self):
        super(HomeTab, self).__init__()

        label = utils.createLabelCText ("Welcome", self, 0, 0)
