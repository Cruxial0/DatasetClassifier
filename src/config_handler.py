from typing import Literal
import yaml

default_colors = {
    "accent_color": "#5a9bd8",
    "alternate_color": "#b08463",
    "warning_color": "#d93f00",
    "select_color": "#8c949a",
    "add_color": "#6b8e6b"
}

default_options = {
    "hide_scored_images": False,
    "auto_scroll_on_scoring": True,
    "treat_categories_as_scoring": False,
    "write_to_filesystem": False
}

default_keybinds = {
    "key_0": "A", # score_9
    "key_1": "S", # score_8_up
    "key_2": "D", # score_7_up
    "key_3": "F", # score_6_up
    "key_4": "G",# score_5_up
    "key_5": "H", # score_7_up
    "key_6": "J",
    "key_7": "K",
    "key_8": "L",
    "key_9": ";",
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
        return self.config.get('keybindings', default_keybinds)

    def get_color(self, color: Literal["accent_color", "alternate_color", "warning_color", "select_color", "add_color"]):
        colors = self.config.get('colors', {})
        # Return the color if found in the config's colors section; otherwise, return the default
        return colors.get(color, default_colors[color])
    
    def set_color(self, color: Literal["accent_color", "alternate_color", "warning_color", "select_color", "add_color"], hex_code):
        colors = self.config.get('colors', {})
        colors[color] = hex_code
        self.config['colors'] = colors

    def get_option(self, option):
        options = self.config.get('options', {})
        return options.get(option, default_options[option])
    
    def set_option(self, option, value):
        options = self.config.get('options', {})
        options[option] = value
        self.config['options'] = options

    def save_config(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)
