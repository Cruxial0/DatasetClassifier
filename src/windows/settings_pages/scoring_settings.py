from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from src.score_presets import get_preset, get_preset_list
from src.windows.settings_pages.settings_widget import SettingsWidget

class ScoringSettingsPage(SettingsWidget):
    def __init__(self, parent=None):
        self.presets = get_preset_list()
        super().__init__(parent)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        scores_combobox = self._create_combobox("Scoring Preset", self.presets, 'scores.preset', callback=self.set_preset)
        
        layout.addLayout(scores_combobox)
        layout.addLayout(self._create_preview_buttons())
        layout.addStretch()

        preset = self.config_handler.get_value('scores.preset')
        _, scores = get_preset(preset)
        self._update_button_names(scores)

    def set_preset(self, preset_name):
        _, scores = get_preset(preset_name)

        self.config_handler.set_scores(scores)
        self.config_handler.save_config()
        
        self._update_button_names(scores)
            
    def _update_button_names(self, scores):
        for i, button in enumerate(self.buttons):
            button.setText(scores[i])

    def _create_preview_buttons(self):
        self.buttons = []
        buttons_layout = QHBoxLayout()
        for i in range(0, 6):
            button = QPushButton()
            button.setObjectName(f'preview_score_{i}')
            buttons_layout.addWidget(button)
            self.buttons.append(button)  # Store button references in a list

        # Add a discard button
        discard_button = QPushButton("discard")
        discard_button.setObjectName('preview_discard')
        buttons_layout.addWidget(discard_button)

        return buttons_layout