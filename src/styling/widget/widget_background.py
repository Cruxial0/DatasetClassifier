from src.config_handler import ConfigHandler
from src.styling.style import Style


STYLE = """
    QWidget {{
        background-color: {};
    }}
"""

class WidgetBackgroundStyle(Style):
    def __init__(self, color=None):
        self.color = "colors.background_color" if color is None else color
        super().__init__()
    def get_style(self, config: ConfigHandler) -> str:
        background_color = config.get_value(self.color)
        return STYLE.format(background_color)
    
class WidgetBackgroundAccentStyle(WidgetBackgroundStyle):
    def __init__(self):
        super().__init__("colors.accent_color")

class WidgetBackgroundWarningStyle(WidgetBackgroundStyle):
    def __init__(self):
        super().__init__("colors.warning_color")