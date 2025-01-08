from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QSpacerItem
from PyQt6.QtGui import QFont
from src.windows.settings_pages.settings_widget import SettingsWidget


class BehaviourSettings(SettingsWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Scoring section
        layout.addLayout(self._create_header("Scoring"))
        layout.addLayout(self._create_checkbox(
            "Auto scroll on scoring",
            "Automatically moves to the next image when a score button is clicked",
            'behaviour.auto_scroll_scores'
        ))
        
        # Tagging section
        layout.addLayout(self._create_header("Tagging", category_break=True))
        layout.addLayout(self._create_checkbox(
            "Auto scroll when TagGroup condition is met",
            "Automatically moves to the next TagGroup when a TagGroup condition is met",
            'behaviour.auto_scroll_on_tag_condition'
        ))
        layout.addLayout(self._create_checkbox(
            "Disable auto-scroll until enabled (⚡/🔅)",
            "If enabled, when temporarily disabling auto-scroll, it will\nremain disabled until re-enabled",
            'behaviour.auto_scroll_disable_until_enabled'
        ))
        layout.addLayout(self._create_checkbox(
            "Use strict mode for 'to latest' (🎯)",
            "If enabled, will ignore the 'is_required' clause,\nand will find the latest TagGroup where 'min_tags' is not met",
            'behaviour.to_latest_strict_mode'
        ))

        layout.addStretch()    
