from src.config_handler import ConfigHandler
from src.styling.color_helper import ColorHelper
from src.styling.style import Style
from src.utils import get_resource_path

STYLE = """
    QSpinBox {{
        background-color: {};
        color: {};
        padding: 5px 10px;
        border-radius: 3px;
    }}
    QSpinBox:hover {{
        background-color: {};
    }}
    QSpinBox:pressed {{
        background-color: {};
    }}
    QSpinBox:disabled {{
        background-color: {};
        color: {};
    }}
    QSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 16px;
        border-width: 1px;
    }}
    QSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 16px;
        border-width: 1px;
    }}
    QSpinBox::up-arrow {{
        width: 7px;
        height: 7px;
        image: url({});
    }}
    QSpinBox::down-arrow {{
        width: 7px;
        height: 7px;
        image: url({});
    }}
"""

class SpinBoxStyle(Style):
    def get_style(self, config: ConfigHandler):
        colors = ColorHelper(config.get_value('colors.button_color')).get_variants()
        return STYLE.format(colors['primary'], config.get_color("text_color"),
                            colors['hover'],
                            colors['active'],
                            config.get_color("disabled_color"), config.get_color("text_color_disabled"),
                            get_resource_path('icons/chevron-up.svg').replace('\\', '/'), get_resource_path('icons/chevron-down.svg').replace('\\', '/'))