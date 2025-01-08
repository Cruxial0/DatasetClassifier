from src.config_handler import ConfigHandler
from src.styling.color_helper import ColorHelper
from src.styling.style import Style


STYLE = """
    QMenuBar {{
        spacing: 3px;
        padding: 5px 5px;
    }}
    QMenuBar::item {{
        background-color: {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
    }}
    QMenuBar::item:selected {{
        background-color: {};
        color: {};
    }}
    
"""


class MenuBarStyle(Style):
    def get_style(self, config: ConfigHandler):
        colors = ColorHelper(config.get_value('colors.panel_color')).get_variants()
        text_color = config.get_value('colors.text_color_overlay')
        return STYLE.format(colors['primary'], text_color, 
                            colors['hover'],text_color, 
                            colors['active'], text_color)