from enum import Enum
from typing import Callable, Dict, Optional, Union
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtGui import QKeySequence, QShortcut
from dataclasses import dataclass

@dataclass
class ConfigBinding:
    """Represents a keybinding configuration with its config path"""
    config_key: str
    description: str
    default_value: str | int

# Define a type for possible binding targets
BindTarget = Union[QPushButton, Callable[[], None]]

class KeybindHandler:
    def __init__(self, config_handler):
        self.config_handler = config_handler
        self.registered_pages: Dict[str, 'KeybindPage'] = {}
        
        # Define all possible keybindings with their config paths and defaults
        self.binding_definitions = {
            'next_image': ConfigBinding(
                config_key='keybindings.next_image',
                description='Next image',
                default_value=16777236  # Right arrow
            ),
            'previous_image': ConfigBinding(
                config_key='keybindings.previous_image',
                description='Previous image',
                default_value=16777234  # Left arrow
            ),
            'discard': ConfigBinding(
                config_key='keybindings.discard',
                description='Discard image',
                default_value=16777219  # Backspace
            ),
            'continue': ConfigBinding(
                config_key='keybindings.continue',
                description='Continue',
                default_value=16777220  # Enter
            ),
            'blur': ConfigBinding(
                config_key='keybindings.blur',
                description='Blur',
                default_value=32  # Space
            ),
            **{
                f'key_{i}': ConfigBinding(
                    config_key=f'keybindings.key_{i}',
                    description=f'Score {i}',
                    default_value=None
                ) for i in range(10)
            }
        }
        
        # Current bindings cache
        self.current_bindings: Dict[str, str | int] = self._load_keybindings()
    
    def _load_keybindings(self) -> Dict[str, str | int]:
        """Load keybindings from config"""
        bindings = {}
        for action, binding in self.binding_definitions.items():
            value = self.config_handler.get_value(binding.config_key)
            bindings[action] = value if value is not None else binding.default_value
        return bindings
    
    def register_page(self, page_id: str, page: 'KeybindPage'):
        """Register a page to receive keybinding updates"""
        self.registered_pages[page_id] = page
        page.apply_keybindings(self.current_bindings)
    
    def unregister_page(self, page_id: str):
        """Unregister a page"""
        if page_id in self.registered_pages:
            del self.registered_pages[page_id]
    
    def update_keybinding(self, action: str, new_value: str | int):
        """Update a keybinding and propagate changes to all pages"""
        if action in self.binding_definitions:
            binding = self.binding_definitions[action]
            # Update config
            self.config_handler.set_value(binding.config_key, new_value)
            # Update cache
            self.current_bindings[action] = new_value
            # Update all registered pages
            for page in self.registered_pages.values():
                page.apply_keybindings(self.current_bindings)
    
    def unregister_keybinding(self, action: str):
        """Unregister a keybinding and remove it from all pages"""
        if action in self.current_bindings:
            # Remove from current bindings
            del self.current_bindings[action]
            
            # Update all registered pages to remove this binding
            for page in self.registered_pages.values():
                page.remove_keybinding(action)


class KeybindPage:
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.shortcuts: Dict[str, QShortcut] = {}
        self.bindings: Dict[str, Optional[BindTarget]] = {}

    def register_binding(self, action: str, target: Optional[BindTarget] = None):
        """Register a button or function to be bound to a specific key action"""
        self.bindings[action] = target
        # Reapply keybindings if the target is being set
        if target is not None:
            self.apply_keybindings({action: self.shortcuts.get(action)})

    def register_button_binding(self, action: str, button: Optional[QPushButton] = None):
        """Legacy method for backwards compatibility"""
        self.register_binding(action, button)

    def apply_keybindings(self, bindings: Dict[str, str | int]):
        """Apply keybindings to this page's buttons or functions"""
        # Clear only the shortcuts we're updating
        for action in bindings:
            if action in self.shortcuts:
                shortcut = self.shortcuts[action]
                shortcut.setEnabled(False)
                shortcut.deleteLater()
                del self.shortcuts[action]
        
        for action, key in bindings.items():
            if action in self.bindings and self.bindings[action] is not None:
                target = self.bindings[action]
                
                # Skip if either target or key is None
                if target is None or key is None:
                    continue

                def create_handler(target: BindTarget):
                    if isinstance(target, QPushButton):
                        def handler():
                            if target.isEnabled():
                                target.click()
                    else:  # Callable
                        handler = target
                    return handler

                # Create shortcut with properly bound handler
                shortcut = QShortcut(QKeySequence(key), self.widget)
                shortcut.activated.connect(create_handler(target))
                self.shortcuts[action] = shortcut

                # For Alt+key shortcuts (category buttons)
                if action.startswith('key_'):
                    alt_shortcut = QShortcut(
                        QKeySequence(f"Alt+{key}"), 
                        self.widget
                    )
                    alt_shortcut.activated.connect(create_handler(target))
                    self.shortcuts[f"alt_{action}"] = alt_shortcut

    def remove_keybinding(self, action: str):
        """Remove a specific keybinding"""
        # Clear the shortcut if it exists
        if action in self.shortcuts:
            shortcut = self.shortcuts[action]
            shortcut.setEnabled(False)
            shortcut.deleteLater()
            del self.shortcuts[action]
            
        # Also clear alt shortcut if it exists
        alt_action = f"alt_{action}"
        if alt_action in self.shortcuts:
            alt_shortcut = self.shortcuts[alt_action]
            alt_shortcut.setEnabled(False)
            alt_shortcut.deleteLater()
            del self.shortcuts[alt_action]

    def _clear_shortcuts(self):
        for shortcut in self.shortcuts.values():
            shortcut.setEnabled(False)
            shortcut.deleteLater()
        self.shortcuts.clear()