from typing import Dict, List
from src.keybinds.keybind_manager import KeyBinding, KeybindPage


class ScoringKeybindPage(KeybindPage):
    """Specialized KeybindPage for scoring functionality"""
    def __init__(self, scoring_page):
        super().__init__(scoring_page)
        self.scoring_page = scoring_page

    def apply_keybindings(self, bindings: Dict[str, List[KeyBinding]]):
        """Override to update button labels when keybindings change"""
        super().apply_keybindings(bindings)
        self.scoring_page.update_score_button_labels()
        self.scoring_page.update_category_button_labels()