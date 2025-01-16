from src.config_handler import ConfigHandler
from src.styling.style import Style
from src.styling.color_helper import ColorHelper

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

class AcceptButtonStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        colors = ColorHelper(config.get_value('colors.accent_color')).get_variants()
        text_color = config.get_value('colors.text_color')
        disabled = config.get_value('colors.disabled_color')
        text_color_disabled = config.get_value('colors.text_color_disabled')
        return STYLE.format(colors['primary'], text_color, colors['hover'], colors['active'], disabled, text_color_disabled)
    
class RejectButtonStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        colors = ColorHelper(config.get_value('colors.warning_color')).get_variants(0.4, 0.7)
        text_color = config.get_value('colors.text_color')
        disabled = config.get_value('colors.disabled_color')
        text_color_disabled = config.get_value('colors.text_color_disabled')
        return STYLE.format(colors['primary'], text_color, colors['hover'], colors['active'], disabled, text_color_disabled)