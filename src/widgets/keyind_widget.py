from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal, QEvent
from PyQt6.QtGui import QKeySequence

class KeybindWidget(QPushButton):
    keyPressed = pyqtSignal(int)

    def __init__(self, key=0, parent=None):
        super().__init__(parent)
        self.key = key
        self.setText(self.get_key_name(key) or "Press a key")
        self.setCheckable(True)
        self.clicked.connect(self.start_capture)
        self.installEventFilter(self)
        self.is_capturing = False

    def get_key_name(self, keycode):
        if keycode == 0:
            return "None"
        return QKeySequence(keycode).toString()

    def eventFilter(self, obj, event):
        if self.is_capturing and event.type() == QEvent.Type.KeyPress:
            self.key = event.key()
            self.setText(self.get_key_name(self.key))
            self.setChecked(False)
            self.is_capturing = False
            self.keyPressed.emit(self.key)
            return True
        return super().eventFilter(obj, event)

    def start_capture(self):
        self.setChecked(True)
        self.is_capturing = True