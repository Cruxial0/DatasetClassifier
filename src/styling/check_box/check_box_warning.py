import os
import tempfile

from src.config_handler import ConfigHandler
from src.styling.style import Style

# Define the SVG template with a placeholder for fill color
CHECKMARK_SVG_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <path fill="{}" d="M13.5 4.5L6 12l-4-4 1.5-1.5L6 9.586l6-6L13.5 4.5z"/>
</svg>
"""

STYLE = """
QCheckBox {{
    color: {};
    font-weight: bold;
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

class CheckBoxWarningStyle(Style):
    def __init__(self, text_color="colors.warning_color", border_color="colors.button_border_color"):
        self.text_color = text_color
        self.border_color = border_color
        super().__init__()

    def get_style(self, config: ConfigHandler) -> str:
        text_color = config.get_value(self.text_color)
        border_color = config.get_value(self.border_color)
        
        customized_svg = CHECKMARK_SVG_TEMPLATE.format(text_color)
        
        # Create a temporary file for the SVG. This is fucking disgusting, but I can't find a proper way to do it.
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as temp_file:
            temp_file.write(customized_svg.encode('utf-8'))
            checkmark_url = os.path.abspath(temp_file.name)
        
        return STYLE.format(text_color, border_color, text_color, border_color, checkmark_url)