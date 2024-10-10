from typing import Literal
import yaml

default_colors = {
    "accent_color": "#5a9bd8",
    "alternate_color": "#b08463",
    "warning_color": "#d93f00",
    "select_color": "#8c949a",
    "add_color": "#6b8e6b"
}

class ConfigHandler:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    def get_keybindings(self):
        return self.config.get('keybindings', {})

    def get_color(self, color: Literal["accent_color", "alternate_color", "warning_color", "select_color", "add_color"]):
        colors = self.config.get('colors', {})
        # Return the color if found in the config's colors section; otherwise, return the default
        return colors.get(color, default_colors[color])
    
    def set_color(self, color: Literal["accent_color", "alternate_color", "warning_color", "select_color", "add_color"], hex_code):
        colors = self.config.get('colors', {})
        colors[color] = hex_code
        self.config['colors'] = colors

    def get_use_copy_category(self):
        return self.config.get('use_copy_custom')
    
    def get_use_copy_default(self):
        return self.config.get('use_copy_default')

    def get_treat_categories_as_scoring(self):
        return self.config.get('treat_categories_as_scoring', False)

    def set_use_copy_category(self, value):
        self.config['use_copy_custom'] = value

    def set_use_copy_default(self, value):
        self.config['use_copy_default'] = value

    def set_treat_categories_as_scoring(self, value):
        self.config['treat_categories_as_scoring'] = value

    def get_auto_scroll_on_scoring(self):
        return self.config.get('auto_scroll_on_scoring', False)

    def set_auto_scroll_on_scoring(self, value):
        self.config['auto_scroll_on_scoring'] = value

    def save_config(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)
