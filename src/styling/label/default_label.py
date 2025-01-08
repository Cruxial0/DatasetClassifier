from src.config_handler import ConfigHandler
from src.styling.style import Style


class LabelStyle(Style):
    def __init__(self, bold=False):
        self.bold = bold
        super().__init__()
    def get_style(self, config: ConfigHandler) -> str:
        text_color = config.get_value('colors.text_color')
        return f"color: {text_color}" if not self.bold else f"color: {text_color}; font-weight: bold;"

class SubtextLabelStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        text_color = config.get_value('colors.text_color_overlay')
        return f"color: {text_color}"