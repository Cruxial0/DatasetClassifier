from PyQt6.QtGui import QKeySequence
from typing import Dict, List

from src.keybinds.keybind_manager import KeyBinding, KeybindPage


class TaggingKeybindPage(KeybindPage):
    """Specialized KeybindPage for tagging functionality"""
    def __init__(self, tagging_page):
        super().__init__(tagging_page)
        self.tagging_page = tagging_page
    
    def apply_keybindings(self, bindings: Dict[str, List[KeyBinding]]):
        """Override to update button labels when keybindings change"""
        super().apply_keybindings(bindings)

    def _create_key_sequence(self, binding: KeyBinding) -> QKeySequence:
        """Create a QKeySequence from a KeyBinding"""
        key = binding.key
        if binding.modifiers:
            modifier_str = "+".join(mod.name.replace('KeyboardModifier.', '') 
                                  for mod in binding.modifiers)
            return QKeySequence(f"{modifier_str}+{key}")
        return QKeySequence(key)