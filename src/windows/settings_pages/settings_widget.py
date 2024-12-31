from typing import Any, Callable
from PyQt6.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QSpinBox, QSpacerItem
from PyQt6.QtGui import QFont
from abc import abstractmethod

from src.database.database import Database
from src.project import Project
from src.config_handler import ConfigHandler
from src.update_poller import UpdatePoller

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db: Database = parent.db
        self.config_handler: ConfigHandler = parent.config_handler
        self.update_poller: UpdatePoller = parent.update_poller
        self.active_project: Project = parent.active_project

        self.init_ui()

    def init_ui(self):
        """
        Initializes the UI of the settings widget. This is called when the widget is instantiated and should be overridden
        by subclasses to create the UI for the specific settings page.
        """
        pass

    @abstractmethod
    def navigate_path(self, path: str):
        
        """
        Navigates to the given path in the settings widget. This is an abstract method and must be overridden by subclasses.
        
        Args:
            path (str): The path to navigate to (dot notation).
        """
        pass

    def set_value(self, path: str, value: Any):
        self.config_handler.set_value(path, value)
        self.config_handler.save_config()

    def get_key_name(self, key: str):
        formatted = key.lower().replace(' ', '_')
        if formatted.startswith('key_'):
            index = int(formatted.split('_')[1]) - 1
            return f"key_{index}"
        return formatted
    



    # Helper functions
    def _create_header(self, text: str, category_break: bool = False) -> QVBoxLayout:
        layout = QVBoxLayout()
        if category_break:
            layout.addSpacerItem(QSpacerItem(0, 20))
        label = QLabel(text)
        label.setObjectName(f"settings_page_{text.replace(' ', '_').lower()}_label")
        label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(label)
        layout.addSpacerItem(QSpacerItem(0, 10))
        return layout
    
    def _create_checkbox(self, text: str, tooltip: str, setting: str, callback: Callable[[bool], None] = None) -> QCheckBox:
        """Creates a checkbox for the given setting and connects it to the given callback.
        
        Args:
            text (str): The text to display next to the checkbox.
            tooltip (str): The tooltip to display when hovering over the checkbox.
            setting (str): The configuration setting to read and write to.
            callback (Callable[[bool], None], optional): The callback to call when the checkbox's state changes. Defaults to None.
        
        Returns:
            QCheckBox: The created checkbox.
        """
        
        checkbox = QCheckBox(text, self)
        checkbox.setToolTip(tooltip)
        print(f"Setting {setting} to {self.config_handler.get_value(setting)}")
        checkbox.setChecked(self.config_handler.get_value(setting))
        
        def on_change(state):
            is_checked = state.value > 0
            self.set_value(setting, is_checked)
            if callback:
                callback(is_checked)
        
        checkbox.checkStateChanged.connect(on_change)
        return checkbox
    
    def _create_combobox(self, label: str, items: list, setting: str, callback: Callable[[str], None] = None) -> QHBoxLayout:
        """Creates a combobox for the given setting and connects it to the given callback.
        
        Args:
            label (str): The label to display next to the combobox.
            items (list): The items to display in the combobox.
            setting (str): The configuration setting to read and write to.
            callback (Callable[[str]], optional): The callback to call when the combobox's current text changes. Defaults to None.
        
        Returns:
            QHBoxLayout: A horizontal layout containing the label and the combobox.
        """

        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        combo_box = QComboBox()
        combo_box.addItems(items)
        combo_box.setCurrentText(self.config_handler.get_value(setting))

        def on_change(text):
            self.set_value(setting, text)
            if callback:
                callback(text)

        combo_box.currentTextChanged.connect(on_change)
        layout.addWidget(combo_box)
        return layout
    
    def _create_spinbox(self, label: str, setting: str, mix_max: tuple[int, int], callback: Callable[[int], None] = None) -> QHBoxLayout:
        """Creates a SpinBox for the given setting and connects it to the given callback.
    
        Args:
            label (str): The label to display next to the SpinBox.
            setting (str): The configuration setting to read and write to.
            mix_max (tuple[int, int]): The minimum and maximum values for the SpinBox.
            callback (Callable[[int], None], optional): The callback to call when the SpinBox's value changes. Defaults to None.
    
        Returns:
            QHBoxLayout: A horizontal layout containing the label and the SpinBox.
        """
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        spinbox = QSpinBox()
        spinbox.setRange(mix_max[0], mix_max[1])
        spinbox.setValue(self.config_handler.get_value(setting))
        
        spinbox.valueChanged.connect(lambda value: self.set_value(setting, value))
        layout.addWidget(spinbox)
        return layout