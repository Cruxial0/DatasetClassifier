from src.config_handler import ConfigHandler
from src.styling.style import Style


STYLE = """
    QWidget {{
        background-color: {}; 
        border-radius: 8px;
    }}
"""

class PanelWidgetStyle(Style):
    def __init__(self, color = "colors.panel_color"):
        self.color = color
        super().__init__()
    def get_style(self, config: ConfigHandler) -> str:
        background_color = config.get_value(self.color)
        return STYLE.format(background_color)