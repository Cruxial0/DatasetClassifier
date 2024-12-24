from typing import Literal
import yaml

from src.score_presets import get_preset

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
    "key_4": "G", # score_5_up
    "key_5": "H", # score_4_up
    "key_6": "J",
    "key_7": "K",
    "key_8": "L",
    "key_9": ";",
    "discard": "BACKSPACE",
    "image_next": "Right",
    "image_previous": "Left"
}

default_export_options = {
    "export_captions": False,
    "seperate_by_score": False,
    "delete_images": False
}

default_scores = {
    "preset": "pdxl",
    "score_0": "score_9",
    "score_1": "score_8_up",
    "score_2": "score_7_up",
    "score_3": "score_6_up",
    "score_4": "score_5_up",
    "score_5": "score_4_up"
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
    
    def set_keybind(self, key, value):
        keybinds = self.config.get('keybindings', default_keybinds)
        keybinds[key] = value
        self.config['keybindings'] = keybinds

    def get_colors(self):
        return self.config.get('colors', default_colors)

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

    def get_export_option(self, export_option):
        export_options = self.config.get('export_options', default_export_options)
        return export_options.get(export_option, default_export_options[export_option])
    
    def set_export_option(self, export_option, value):
        export_options = self.config.get('export_options', default_export_options)
        export_options[export_option] = value
        self.config['export_options'] = export_options

    def get_scores(self) -> tuple[str, dict[str, str]]:
        scores = self.config.get('scores', default_scores)
        score_list = {}
        for i in range(0, 6):
            score_list[f'score_{i}'] = scores[f'score_{i}']
        
        return scores.get('preset', default_scores["preset"]), score_list
    
    def get_score(self, score):
        scores = self.config.get('scores', default_scores)
        return scores.get(score, default_scores[score])
    
    def set_scores(self, values: list[str]):
        if len(values) != 6:
            return
        
        scores = self.config.get('scores', default_scores)
        for i in range(0, 6):
            scores[f'score_{i}'] = values[i]

        self.config['scores'] = scores
    
    def set_scores_preset(self, preset_name):
        preset, values = get_preset(preset_name)
        scores = self.config.get('scores', default_scores)
        for i in range(0, 6):
            scores[f'score_{i}'] = values[i]

        scores['preset'] = preset

        self.config['scores'] = scores

    def get_selected_preset(self):
        scores = self.config.get('scores', default_scores)
        return scores.get('preset', default_scores["preset"])

    def save_config(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)
