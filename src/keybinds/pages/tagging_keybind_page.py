from typing import Dict
from src.keybinds.keybind_manager import KeybindPage

class TaggingKeybindPage(KeybindPage):
    """Specialized KeybindPage for scoring functionality"""
    def __init__(self, tagging_page):
        super().__init__(tagging_page)
        self.tagging_page = tagging_page
    
    def apply_keybindings(self, bindings: Dict[str, str | int]):
        """Override to update button labels when keybindings change"""
        super().apply_keybindings(bindings)
        # self.tagging_page.update_score_button_labels()