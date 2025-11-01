import tempfile
from pathlib import Path

from src.config_handler import ConfigHandler
from src.styling.style import Style

CHECKMARK_SVG_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <path fill="{}" d="M13.5 4.5L6 12l-4-4 1.5-1.5L6 9.586l6-6L13.5 4.5z"/>
</svg>
"""

STYLE = """
QCheckBox {{
    color: {};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    background-color: transparent;
    border: 1px solid {};
}}
QCheckBox::indicator:checked {{
    color: {};
    border: 1px solid {};
    image: url({});
}}
"""

class CheckBoxStyle(Style):
    def __init__(self, text_color="colors.text_color_overlay", icon_color="colors.text_color", border_color="colors.button_border_color"):
        self.text_color = text_color
        self.icon_color = icon_color
        self.border_color = border_color
        super().__init__()

    def get_style(self, config: ConfigHandler) -> str:
        text_color = config.get_value(self.text_color)
        icon_color = config.get_value(self.icon_color)
        border_color = config.get_value(self.border_color)

        customized_svg = CHECKMARK_SVG_TEMPLATE.format(icon_color)

        # Create a temporary file for the SVG
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(customized_svg)
            temp_path = temp_file.name

        # Convert to Qt-compatible URL format (forward slashes, proper escaping)
        checkmark_url = Path(temp_path).as_posix()

        return STYLE.format(text_color, border_color, text_color, border_color, checkmark_url)
