from src.config_handler import ConfigHandler
from src.styling.style import Style
from src.styling.line_edit.line_edit import LineEditStyle

STYLE = """
    TagSearchWidget > {}
    TagSearchWidget > QScrollArea {{
        border: none;
        background-color: {};
        color: {};
        border-radius: 3px;
    }}
    """

class TagSearchStyle(Style):
    def get_style(self, config: ConfigHandler) -> str:
        line_edit_style = LineEditStyle().get_style(config)
        background_color = config.get_value("colors.button_color")
        text_color = config.get_value("colors.text_color_overlay")

        return STYLE.format(line_edit_style,
                            background_color, text_color)
    