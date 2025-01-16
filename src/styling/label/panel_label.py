from src.config_handler import ConfigHandler
from src.styling.style import Style


STYLE = """
    QLabel {{
        background-color: {};
        color: {};
        padding: {};
        border-radius: 3px;
    }}
    """

class PanelLabelStyle(Style):
    def __init__(self, padding = "5px 10px", color = "colors.button_color", text_color = "colors.text_color_overlay"):
        self.color = color
        self.text_color = text_color
        self.padding = padding
        super().__init__()
    def get_style(self, config: ConfigHandler) -> str:
        background_color = config.get_value(self.color)
        text_color = config.get_value(self.text_color)
        return STYLE.format(background_color, text_color, self.padding)
    
class ImageViewerStyle(PanelLabelStyle):
    def __init__(self):
        super().__init__("0px")