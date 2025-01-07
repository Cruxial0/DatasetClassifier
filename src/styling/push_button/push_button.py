from src.config_handler import ConfigHandler
from src.styling.color_helper import ColorHelper
from src.styling.style import Style

STYLE = """
    QPushButton {{
        background-color: {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
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
    def get_style(self, config: ConfigHandler) -> str:
        colors = ColorHelper(config.get_value('colors.button_color')).get_variants()
        text_color = config.get_value('colors.text_color')
        disabled = config.get_value('colors.disabled_color')
        text_color_disabled = config.get_value('colors.text_color_disabled')
        return STYLE.format(colors['primary'], text_color, 
                            colors['hover'], 
                            colors['active'], 
                            disabled, text_color_disabled)