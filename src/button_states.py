from typing import Literal
from PyQt6.QtWidgets import QPushButton


class ButtonStateManager:
    def __init__(self):
        self.score_buttons = []
        self.category_buttons = []
        self.input_buttons = []
        self.image_buttons = []
        self.score_enabled = False
        self.category_enabled = False
        self.input_enabled = False
        self.image_enabled = False

    def toggle_button_group(self, state: bool, group: Literal['score', 'category', 'input', 'image']):
        enabled, buttons = self.get_button_group(group)    
        if enabled == state:
            return
        for btn in buttons:
            if group == 'category':
                self.category_enabled = state

            btn.setEnabled(state)

    def toggle_button(self, state: bool, name, group: Literal['score', 'category', 'input', 'image']):
        enabled, buttons = self.get_button_group(group)
        # if enabled == state:
        #     return
        for btn in buttons:
            if btn.objectName() == name:
                btn.setEnabled(state)

    def declare_button_group(self, buttons, group: Literal['score', 'category', 'input', 'image']):
        if group == 'score':
            self.score_buttons = buttons
        elif group == 'category':
            self.category_buttons = buttons
        elif group == 'input':
            self.input_buttons = buttons
        elif group == 'image':
            self.image_buttons = buttons

    def get_button_group(self, group: Literal['score', 'category', 'input', 'image']) -> tuple[bool, list[QPushButton]]:
        if group == 'score':
            return self.score_enabled, self.score_buttons
        elif group == 'category':
            return self.category_enabled, self.category_buttons
        elif group == 'input':
            return self.input_enabled, self.input_buttons
        elif group == 'image':
            return self.image_enabled, self.image_buttons