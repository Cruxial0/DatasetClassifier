from src.config_handler import ConfigHandler
from src.styling.style import Style


STYLE = """
    QProgressBar {{
        border: 1px solid transparent;
        border-radius: 5px;
        text-align: center;
        background-color: {};
        color: {};
    }}

    QProgressBar::chunk {{
        background-color: {};
        border-radius: 4px;
    }}
"""

class ProgressBarStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        background_color = config.get_value('colors.button_color')
        accent_color = config.get_value('colors.accent_color')
        text_color = config.get_value('colors.text_color')
        return STYLE.format(background_color, text_color, accent_color)