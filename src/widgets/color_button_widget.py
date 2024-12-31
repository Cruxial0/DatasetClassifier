import random
import string
from PyQt6.QtWidgets import QPushButton, QColorDialog
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal

class ColorButton(QPushButton):
    color_changed: pyqtSignal = pyqtSignal(QColor)
    def __init__(self, color=QColor(0, 0, 0), parent=None):
        super().__init__(parent)
        
        alphabet = string.ascii_lowercase + string.digits
        self.name = ''.join(random.choices(alphabet, k=8))
        self.setObjectName(self.name)
        self.color = color
        self.setFixedSize(50, 30)
        self.updateStyle()

    def updateStyle(self):
        self.setStyleSheet(
            f"#{self.name} {{ background-color: {self.color.name()}; }}"
        )

    def chooseColor(self):
        dialog = QColorDialog(self.color, self)
        if dialog.exec() == QColorDialog.DialogCode.Accepted:
            self.color = dialog.currentColor()
            self.updateStyle()

            self.color_changed.emit(self.color)