from src.config_handler import ConfigHandler
from src.styling.style import Style


STYLE = """
    QLabel {{
        background-color: {};
        color: {};
        padding: 5px 5px;
        border-radius: 3px;
        min-width: 25px;
        max-width: 25px;
        qproperty-alignment: AlignCenter;
    }}
"""

class KeybindLabelStyle(Style):
    def __init__(self, color="colors.button_color", text_color="colors.text_color_overlay"):
        self.color = color
        self.text_color = text_color
        super().__init__()
    def get_style(self, config: ConfigHandler) -> str:
        background_color = config.get_value(self.color)
        text_color = config.get_value(self.text_color)
        return STYLE.format(background_color, text_color)
    
class KeybindLabelAccentStyle(KeybindLabelStyle):
    def __init__(self):
        super().__init__("colors.accent_color", "colors.text_color")

class KeybindLabelDisabledStyle(KeybindLabelStyle):
    def __init__(self):
        super().__init__("colors.disabled_color", "colors.text_color_disabled")