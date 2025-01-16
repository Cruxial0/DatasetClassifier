from src.config_handler import ConfigHandler
from src.styling.style import Style
from src.styling.color_helper import ColorHelper

STYLE = """
    QPushButton {{
        background-color: {};
        border: 1px solid {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
        height: 30px;
        font-family: Arial;
    }}
    QPushButton:checked {{
        background-color: {};
    }}
    QPushButton:unchecked {{
        background-color: {};
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

class MenuButtonStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        btn_color = config.get_value('colors.button_color')
        btn_border_color = config.get_value('colors.button_border_color')
        colors = ColorHelper(config.get_value('colors.accent_color')).get_variants()
        text_color = config.get_value('colors.text_color')
        disabled = config.get_value('colors.disabled_color')
        text_color_disabled = config.get_value('colors.text_color_disabled')
        return STYLE.format(
            btn_color, btn_border_color, text_color, 
            colors['primary'], 
            colors['primary'], 
            colors['hover'], 
            colors['active'], 
            disabled, text_color_disabled
        )
