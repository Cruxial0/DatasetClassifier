from src.config_handler import ConfigHandler
from src.styling.style import Style


STYLE = """
    QLineEdit {{
        background-color: {};
        border: 1px solid {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
    }}
    """

class LineEditStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        background_color = config.get_value('colors.button_color')
        border_color = config.get_value('colors.button_border_color')
        text_color = config.get_value('colors.text_color_overlay')
        return STYLE.format(background_color, border_color, text_color)