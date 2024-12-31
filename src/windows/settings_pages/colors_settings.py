from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QColor
from src.widgets.color_button_widget import ColorButton
from src.windows.settings_pages.settings_widget import SettingsWidget

class ColorsSettingsPage(SettingsWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        loaded_colors = self.config_handler.get_colors()
        colors = {
            "Accent Color": QColor.fromString(loaded_colors['accent_color']),
            "Add Color": QColor.fromString(loaded_colors['add_color']),
            "Alternate Color": QColor.fromString(loaded_colors['alternate_color']),
            "Select Color": QColor.fromString(loaded_colors['select_color']),
            "Warning Color": QColor.fromString(loaded_colors['warning_color'])
        }
        
        for name, color in colors.items():
            row = QHBoxLayout()
            label = QLabel(name, self)
            label.setFixedWidth(100)
            color_button = ColorButton(color, self)
            color_button.clicked.connect(lambda _, cb=color_button: cb.chooseColor())

            color_button.color_changed.connect(lambda c: self.set_color(name, c))
            row.addWidget(label)
            row.addWidget(color_button)
            row.addStretch()
            layout.addLayout(row)

        layout.addStretch(1)

    def set_color(self, name: str, color: QColor):
        self.config_handler.set_color(self.get_key_name(name), color.name(format=QColor.NameFormat.HexRgb))
        self.config_handler.save_config()