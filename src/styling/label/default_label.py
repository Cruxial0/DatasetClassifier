from src.config_handler import ConfigHandler
from src.styling.style import Style


class LabelStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        text_color = config.get_value('colors.text_color')
        return f"color: {text_color}"