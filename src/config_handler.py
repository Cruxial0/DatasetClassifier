from typing import Literal, Any, Optional
import yaml
import os

from src.score_presets import get_preset

default_behaviours = {
    "auto_scroll_scores": True,
    "auto_scroll_on_tag_condition": True,
    "to_latest_strict_mode": False,
    "auto_scroll_disable_until_enabled": False
}

default_colors = {
    "accent_color": "#5a9bd8",
    "alternate_color": "#b08463",
    "warning_color": "#963535",
    "button_color": "#353535",
    "button_border_color": "#444444",
    "button_color_overlay": "#5a9bd8",
    "button_border_color_overlay": "#5a9bd8",
    "disabled_color": "#353535",
    "text_color": "#ffffff",
    "text_color_disabled": "#545454",
    "text_color_overlay": "#c8c8c8",
    "background_color": "#1e1e1e",
    "panel_color": '#292929'
}

default_keybinds = {
    "key_0": "A",  # score_9
    "key_1": "S",  # score_8_up
    "key_2": "D",  # score_7_up
    "key_3": "F",  # score_6_up
    "key_4": "G",  # score_5_up
    "key_5": "H",  # score_4_up
    "key_6": "J",
    "key_7": "K",
    "key_8": "L",
    "key_9": ";",
    "discard": "BACKSPACE",
    "continue": "Return",
    "next_image": "Right",
    "previous_image": "Left",
    "blur": "Space"
}

default_export_options = {
    "export_captions": True,
    "caption_format": ".txt",
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

default_privacy = {
    "blur_strength": 35
}

# Combined defaults for get_value lookup
DEFAULT_VALUES = {
    "behaviour": default_behaviours,
    "colors": default_colors,
    "keybindings": default_keybinds,
    "export_options": default_export_options,
    "scores": default_scores,
    "privacy": default_privacy
}

class ConfigHandler:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Load config from file or create new one with defaults if it doesn't exist"""
        if not os.path.exists(self.config_file):
            # Create new config file with default values
            self._create_default_config()
            return DEFAULT_VALUES.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config is None:
                    loaded_config = {}
                
                # Update config with any missing fields
                updated_config = self._update_missing_fields(loaded_config, DEFAULT_VALUES)
                
                # If we added any missing fields, save the updated config
                if updated_config != loaded_config:
                    with open(self.config_file, 'w') as f:
                        yaml.dump(updated_config, f, sort_keys=False)
                    print(f"Updated config file with missing fields at: {self.config_file}")
                    
                return updated_config
            
        except Exception as e:
            print(f"Error loading config file: {e}")
            return DEFAULT_VALUES.copy()

    def get_value(self, path: str) -> Any:
        """Get a value from config using dot notation with fallback to defaults"""
        current = self.config
        default = DEFAULT_VALUES
        
        for key in path.split('.'):
            # Try to get from actual config first
            if isinstance(current, dict) and key in current:
                current = current[key]
            # Fall back to defaults if not found
            elif isinstance(default, dict) and key in default:
                current = default[key]
            else:
                return None
            
            # Update default fallback path
            default = default.get(key, {}) if isinstance(default, dict) else {}
            
        return current

    def set_value(self, path: str, value: Any):
        """Set a value in config using dot notation"""
        current = self.config
        keys = path.split('.')
        
        # Navigate to the correct nested level
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        # Set the value
        current[keys[-1]] = value

    # Updated convenience methods using dot notation
    def get_keybindings(self):
        return self.get_value('keybindings') or default_keybinds
    
    def set_keybind(self, key: str, value: str):
        self.set_value(f'keybindings.{key}', value)

    def get_colors(self):
        return self.get_value('colors') or default_colors

    def get_color(self, color: str):
        return self.get_value(f'colors.{color}')
    
    def set_color(self, color: str, hex_code: str):
        self.set_value(f'colors.{color}', hex_code)

    def get_option(self, option: str):
        return self.get_value(f'options.{option}')
    
    def set_option(self, option: str, value: Any):
        self.set_value(f'options.{option}', value)

    def get_export_option(self, export_option: str):
        return self.get_value(f'export_options.{export_option}')
    
    def set_export_option(self, export_option: str, value: Any):
        self.set_value(f'export_options.{export_option}', value)

    def get_scores(self) -> tuple[str, dict[str, str]]:
        score_list = {}
        for i in range(6):
            score_key = f'score_{i}'
            score_list[score_key] = self.get_value(f'scores.{score_key}')
        
        return self.get_value('scores.preset'), score_list
    
    def get_score(self, score: str):
        return self.get_value(f'scores.{score}')
    
    def set_scores(self, values: list[str]):
        if len(values) != 6:
            return
        
        for i in range(6):
            self.set_value(f'scores.score_{i}', values[i])

    def set_scores_preset(self, preset_name: str):
        preset, values = get_preset(preset_name)
        
        self.set_value('scores.preset', preset)
        for i in range(6):
            self.set_value(f'scores.score_{i}', values[i])

    def get_selected_preset(self):
        return self.get_value('scores.preset')

    def save_config(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, sort_keys=False)

    def _create_default_config(self):
        """Create a new config file with default values"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(DEFAULT_VALUES, f, sort_keys=False)
            print(f"Created new config file with default values at: {self.config_file}")
        except Exception as e:
            print(f"Error creating default config file: {e}")

    def _update_missing_fields(self, current_config: dict, default_config: dict) -> dict:
        """Recursively update config dictionary with any missing fields from defaults"""
        updated_config = current_config.copy()
        
        for key, default_value in default_config.items():
            if key not in updated_config:
                updated_config[key] = default_value
            elif isinstance(default_value, dict) and isinstance(updated_config[key], dict):
                # Recursively update nested dictionaries
                updated_config[key] = self._update_missing_fields(updated_config[key], default_value)
                
        return updated_config