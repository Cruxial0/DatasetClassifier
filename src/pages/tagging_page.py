from PyQt6.QtWidgets import QWidget
from button_states import ButtonStateManager
from config_handler import ConfigHandler
from database.database import Database

class TaggingPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.button_states: ButtonStateManager = parent.button_states
        self.db: Database = parent.db
        self.config_handler: ConfigHandler = parent.config_handler
        self.active_project = None

        self.setupUI()

    def setupUI(self):
        pass