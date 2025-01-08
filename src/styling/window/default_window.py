from src.config_handler import ConfigHandler
from src.styling.style import Style


STYLE = """
    QMainWindow > QWidget {{
        background-color: {};
    }}
"""

class DefaultWindowStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        background_color = config.get_value('colors.background_color')
        return STYLE.format(background_color)