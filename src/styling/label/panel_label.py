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
    def __init__(self, padding = "5px 10px"):
        self.padding = padding
        super().__init__()
    def get_style(self, config: ConfigHandler) -> str:
        background_color = config.get_value('colors.button_color')
        text_color = config.get_value('colors.text_color_overlay')
        return STYLE.format(background_color, text_color, self.padding)
    
class ImageViewerStyle(PanelLabelStyle):
    def __init__(self):
        super().__init__("0px")