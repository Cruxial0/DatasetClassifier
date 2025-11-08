from src.config_handler import ConfigHandler
from src.styling.style import Style

STYLE = """
QGroupBox {{
    border: 1px solid {};
    padding: 25px 10px 10px 10px;
    border-radius: 15px;
    margin-top: 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    top: 0px;
    padding: 2px 10px;
    color: {};
    background-color: {};
    border-radius: 5px;
}}
"""

class GroupBoxStyle(Style):
    def __init__(self, text_color="colors.text_color", background_color="colors.background_color", border_color="colors.button_border_color"):
        self.text_color = text_color
        self.background_color = background_color
        self.border_color = border_color
        super().__init__()
    
    def get_style(self, config: ConfigHandler) -> str:
        text_color = config.get_value(self.text_color)
        background_color = config.get_value(self.background_color)
        border_color = config.get_value(self.border_color)
        
        return STYLE.format(border_color, text_color, background_color)