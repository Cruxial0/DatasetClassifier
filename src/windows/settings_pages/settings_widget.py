from PyQt6.QtWidgets import QWidget
from abc import abstractmethod

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    @abstractmethod
    def navigate_path(self, path: str):
        pass