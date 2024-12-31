from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from src.widgets.keyind_widget import KeybindWidget
from src.windows.settings_pages.settings_widget import SettingsWidget

class KeybindSettingsPage(SettingsWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        layout = QVBoxLayout(self)
        loaded_keybinds = self.config_handler.get_keybindings()
        keybinds = {
            "Key 1": loaded_keybinds['key_0'], 
            "Key 2": loaded_keybinds['key_1'], 
            "Key 3": loaded_keybinds['key_2'], 
            "Key 4": loaded_keybinds['key_3'], 
            "Key 5": loaded_keybinds['key_4'],
            "Key 6": loaded_keybinds['key_5'], 
            "Key 7": loaded_keybinds['key_6'], 
            "Key 8": loaded_keybinds['key_7'], 
            "Key 9": loaded_keybinds['key_8'], 
            "Key 10": loaded_keybinds['key_9'],
            "Continue": loaded_keybinds['continue'],
            "Discard": loaded_keybinds['discard'], 
            "Next Image": loaded_keybinds['next_image'], 
            "Previous Image": loaded_keybinds['previous_image'],
            "Blur": loaded_keybinds['blur']
        }
        
        layout.addLayout(self._create_header("Keybinds"))

        for key, value in keybinds.items():
            row = QHBoxLayout()
            label = QLabel(key)
            label.setFixedWidth(100)
            keybind_widget = KeybindWidget(value)
            keybind_widget.keyPressed.connect(lambda k, k_name=self.get_key_name(key): self.update_keybind(k_name, k))
            row.addWidget(label)
            row.addWidget(keybind_widget)
            layout.addLayout(row)
        
        layout.addStretch()

    def update_keybind(self, key_name, key):
        # Update the keybindings in the config handler
        self.config_handler.set_value(f"keybindings.{key_name}", key)
        self.config_handler.save_config()