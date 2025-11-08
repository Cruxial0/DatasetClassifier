from src.config_handler import ConfigHandler
from src.styling.style import Style

STYLE = """
    LogicGroupWidget {{
        border-left-width: 4px;
        border-left-color: {};
        border-left-style: solid;
        border-top-left-radius: 8px;
        border-bottom-left-radius: 8px;
        background-color: {};
        padding-left: 8px;
    }}
"""

class WidgetCurvedOutlineStyle(Style):
    def __init__(self, border_color="colors.accent_color", background_color="colors.background_color"):
        self.border_color = border_color
        self.background_color = background_color
        super().__init__()

    def get_style(self, config: ConfigHandler) -> str:
        border_color = config.get_value(self.border_color)
        background_color = config.get_value(self.background_color)
        return STYLE.format(border_color, background_color)