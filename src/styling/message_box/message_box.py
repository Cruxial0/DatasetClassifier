from src.config_handler import ConfigHandler
from src.styling.style import Style
from src.styling.color_helper import ColorHelper

STYLE = """
    QMessageBox {{
        background-color: {};
        font-size: 14px;
    }}
    QMessageBox QLabel {{
        color: {};
        font-size: 14px;
    }}
    QMessageBox QPushButton {{
        background-color: {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
    }}
    QMessageBox[messageType="warning"] QPushButton {{
        background-color: {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {};
    }}
    QMessageBox[messageType="warning"] QPushButton::hover {{
        background-color: {}
    }}
"""

class MessageBoxStyle(Style):
    def __init__(self, text_color="colors.text_color_overlay", background_color="colors.background_color", button_color="colors.accent_color", button_text_color="colors.text_color", warning_color="colors.warning_color"):
        self.text_color = text_color
        self.warning_color = warning_color
        self.background_color = background_color
        self.button_color = button_color
        self.button_text_color = button_text_color
        super().__init__()

    def get_style(self, config: ConfigHandler) -> str:
        text_color = config.get_value(self.text_color)
        warning_color = config.get_value(self.warning_color)
        background_color = config.get_value(self.background_color)
        button_color = config.get_value(self.button_color)
        button_text_color = config.get_value(self.button_text_color)

        accent_colors = ColorHelper(button_color).get_variants()
        warning_colors = ColorHelper(warning_color).get_variants()
        
        return STYLE.format(background_color, text_color, accent_colors["primary"], button_text_color, warning_colors["primary"], button_text_color, accent_colors["hover"], warning_colors["hover"])
        