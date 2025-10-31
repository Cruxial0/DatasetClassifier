from src.config_handler import ConfigHandler
from src.styling.style import Style

STYLE = """
    QPushButton {{
        border: 1px solid {};
        border-radius: 4px;
        padding: 5px;
        color: {};
        background-color: transparent;
    }}
    QPushButton:hover {{
        background-color: {};
        color: {};
    }}
"""

class FunctionButtonStyle(Style):
    def __init__(self, color = "colors.button_color_overlay", text_color = "colors.button_color"):
        self.color = color
        self.text_color = text_color
    def get_style(self, config: ConfigHandler) -> str:
        main_color = config.get_value(self.color)
        text_color = config.get_value(self.text_color)
        return STYLE.format(main_color, main_color, 
                            main_color, text_color)