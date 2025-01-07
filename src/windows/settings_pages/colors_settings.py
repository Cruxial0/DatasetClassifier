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
            "Alternate Color": QColor.fromString(loaded_colors['alternate_color']),
            "Warning Color": QColor.fromString(loaded_colors['warning_color']),
            "Disabled Color": QColor.fromString(loaded_colors['disabled_color']),
            "Button Color": QColor.fromString(loaded_colors['button_color']),
            "Button Border Color": QColor.fromString(loaded_colors['button_border_color']),
            "Text Color (Enabled)": QColor.fromString(loaded_colors['text_color']),
            "Text Color (Disabled)": QColor.fromString(loaded_colors['text_color_disabled']),
        }
        
        layout.addLayout(self._create_header("Main Colors"))

        for name, color in colors.items():
            row = QHBoxLayout()
            label = QLabel(name, self)
            label.setFixedWidth(100)
            color_button = ColorButton(name, color, self)

            print(f"setting callback: (name: {name})")
            color_button.color_changed.connect(self.set_color)
            row.addWidget(label)
            row.addWidget(color_button)
            row.addStretch()
            layout.addLayout(row)

        layout.addStretch(1)

    def set_color(self, name: str, color: QColor):
        print(f"raw name: {name}")
        dot_path = f"colors.{self.get_key_name(name)}"
        print(f"path: {dot_path}; color: {color.name(format=QColor.NameFormat.HexRgb)}")
        self.config_handler.set_value(dot_path, color.name(format=QColor.NameFormat.HexRgb))
        self.config_handler.save_config()