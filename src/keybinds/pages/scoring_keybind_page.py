from typing import Dict
from src.keybinds.keybind_manager import KeybindPage


class ScoringKeybindPage(KeybindPage):
    """Specialized KeybindPage for scoring functionality"""
    def __init__(self, scoring_page):
        super().__init__(scoring_page)
        self.scoring_page = scoring_page

    def apply_keybindings(self, bindings: Dict[str, str | int]):
        """Override to update button labels when keybindings change"""
        super().apply_keybindings(bindings)
        self.scoring_page.update_score_button_labels()