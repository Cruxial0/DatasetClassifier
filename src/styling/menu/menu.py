from src.config_handler import ConfigHandler
from src.styling.style import Style
from src.styling.color_helper import ColorHelper


STYLE = """
    QMenu {{
        background-color: {};
        color: {};
        border-radius: 3px;
        padding: 5px 5px;
    }}
    QMenu::item {{
        background-color: transparent;
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
    }}
    QMenu::item:selected {{
        background-color: {};
        color: {};
    }}
    QMenu::item:disabled {{
        background-color: {};
        color: {};
    }}
"""

class MenuStyle(Style):
    def get_style(self, config: ConfigHandler):
        colors = ColorHelper(config.get_value('colors.panel_color')).get_variants()
        text_color = config.get_value('colors.text_color')
        text_color_overlay = config.get_value('colors.text_color_overlay')
        return STYLE.format(colors['primary'], text_color, 
                            text_color_overlay, 
                            colors['active'], text_color, 
                            colors['hover'], text_color)