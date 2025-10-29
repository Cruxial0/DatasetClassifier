from src.config_handler import ConfigHandler
from src.styling.color_helper import ColorHelper
from src.styling.style import Style
from src.utils import get_resource_path

icon_path = get_resource_path('../icons/chevron-down.svg')


STYLE = """
    QComboBox {{
        background-color: {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
    }}
    QComboBox:hover {{
        background-color: {};
    }}
    QComboBox:pressed {{
        background-color: {};
    }}
    QComboBox:disabled {{
        background-color: {};
        color: {};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        border-left-width: 1px;
        border-left-color: {};
        border-left-style: solid;
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {};
        color: {};
        outline: 0;
    }}
    QComboBox::down-arrow {{
        image: url("%s");
        width: 15px;
        height: 15px;
    }}
    QComboBox::down-arrow:on {{
        top: 1px;
        left: 1px;
    }}
""" % icon_path.replace('\\', '/')

class ComboBoxStyle(Style):
    def get_style(self, config: ConfigHandler):
        colors = ColorHelper(config.get_value('colors.button_color')).get_variants()
        return STYLE.format(
            colors['primary'], config.get_color("text_color"),
            colors['hover'],
            colors['active'],
            config.get_color("disabled_color"), config.get_color("text_color_disabled"),
            config.get_color("button_border_color"), 
            colors['primary'], config.get_color("text_color_overlay")
        )