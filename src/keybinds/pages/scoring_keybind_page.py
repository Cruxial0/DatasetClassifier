from typing import Dict, List
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import Qt
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
    
    def _create_key_sequence(self, binding: KeyBinding) -> QKeySequence:
        """
        Create a QKeySequence from a KeyBinding
        
        This overrides the base class method to fix the modifier name mapping.
        The base class uses mod.name which produces "KeyboardModifier.AltModifier"
        but QKeySequence needs "Alt".
        """
        key = binding.key
        if binding.modifiers:
            # Map Qt modifier enums to QKeySequence string format
            modifier_map = {
                Qt.KeyboardModifier.AltModifier: "Alt",
                Qt.KeyboardModifier.ControlModifier: "Ctrl",
                Qt.KeyboardModifier.ShiftModifier: "Shift",
                Qt.KeyboardModifier.MetaModifier: "Meta"
            }
            modifier_strs = [modifier_map.get(mod, mod.name) for mod in binding.modifiers]
            modifier_str = "+".join(modifier_strs)
            return QKeySequence(f"{modifier_str}+{key}")
        return QKeySequence(key)