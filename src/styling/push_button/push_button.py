from src.config_handler import ConfigHandler
from src.styling.color_helper import ColorHelper
from src.styling.style import Style

STYLE = """
    QPushButton {{
        background-color: {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
        font-family: Arial;
    }}
    QPushButton:hover {{
        background-color: {};
    }}
    QPushButton:pressed {{
        background-color: {};
    }}
    QPushButton:disabled {{
        background-color: {};
        color: {};
    }}
"""

class PushButtonStyle(Style):
    def __init__(self, color="colors.button_color", text_color="colors.text_color_overlay"):
        self.color =  color
        self.text_color =  text_color
        super().__init__()
    def get_style(self, config: ConfigHandler) -> str:
        colors = ColorHelper(config.get_value(self.color)).get_variants()
        text_color = config.get_value(self.text_color)
        disabled = config.get_value('colors.disabled_color')
        text_color_disabled = config.get_value('colors.text_color_disabled')
        return STYLE.format(colors['primary'], text_color, 
                            colors['hover'], 
                            colors['active'], 
                            disabled, text_color_disabled)
    
class PushButtonAccentStyle(PushButtonStyle):
    def __init__(self):
        color = "colors.accent_color"
        text_color = "colors.text_color"
        super().__init__(color, text_color)

class PushButtonWarningStyle(PushButtonStyle):
    def __init__(self):
        color = "colors.warning_color"
        text_color = "colors.text_color"
        super().__init__(color, text_color)

class PushButtonPanelStyle(PushButtonStyle):
    def __init__(self):
        color = "colors.panel_color"
        text_color = "colors.text_color_overlay"
        super().__init__(color, text_color)
