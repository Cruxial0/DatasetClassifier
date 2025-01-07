from src.config_handler import ConfigHandler
from src.styling.style import Style
from src.styling.color_helper import ColorHelper

STYLE = """
    QPushButton {{
        background-color: {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
    }}
    QPushButton:pressed {{
        background-color: {};
    }}
    QPushButton:checked {{
        background-color: {};
    }}
    QPushButton:hover {{
        background-color: {};
    }}
    QPushButton:unchecked {{
        background-color: {};
    }}
    QPushButton:disabled {{
        background-color: {};
        color: {};
    }}
"""
class ScoreButtonStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        btn_color = config.get_value('colors.button_color')
        btn_border_color = config.get_value('colors.button_border_color')
        colors = ColorHelper(config.get_value('colors.accent_color')).get_variants()
        text_color = config.get_value('colors.text_color')
        disabled = config.get_value('colors.disabled_color')
        text_color_disabled = config.get_value('colors.text_color_disabled')
        return STYLE.format(
            btn_color, text_color, btn_border_color, 
            colors['primary'],
            colors['active'],
            colors['hover'],
            colors['active'],
            colors['active'],
            disabled, text_color_disabled
        )
    
class DiscardButtonStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        btn_color = config.get_value('colors.button_color')
        btn_border_color = config.get_value('colors.button_border_color')
        colors = ColorHelper(config.get_value('colors.warning_color')).get_variants(0.4, 0.7)
        text_color = config.get_value('colors.text_color')
        disabled = config.get_value('colors.disabled_color')
        text_color_disabled = config.get_value('colors.text_color_disabled')
        return STYLE.format(
            btn_color, text_color, btn_border_color, 
            colors['primary'],
            colors['active'],
            colors['hover'],
            colors['primary'],
            colors['primary'],
            disabled, text_color_disabled
        )