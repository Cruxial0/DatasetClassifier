from src.config_handler import ConfigHandler
from src.styling.style import Style

STYLE = """
    {} {{
        background-color: {};
        alternate-background-color: {};
        color: {};
    }}
    """

class ListViewStyle(Style):
    def __init__(self, target=None):
        self.target = "QListView" if target is None else target
        super().__init__()

    def get_style(self, config: ConfigHandler) -> str:
        alternate_background_color = config.get_color("background_color")
        background_color = config.get_color("button_color")
        text_color = config.get_color("text_color_overlay")
        return STYLE.format(self.target, background_color, alternate_background_color, text_color)
    
class ListWidgetStyle(ListViewStyle):
    def __init__(self):
        super().__init__("QListWidget")