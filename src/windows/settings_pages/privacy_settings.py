from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSpinBox

from src.windows.settings_pages.settings_widget import SettingsWidget

class PrivacySettingsPage(SettingsWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addLayout(self._create_header("Privacy"))
        blur_strength_spinbox = self._create_spinbox("Blur Strength", "privacy.blur_strength", (0, 100))
        lbl = QLabel("(0 - 100) (requires restart)")
        lbl.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'subtext'))
        blur_strength_spinbox.addWidget(lbl)
        blur_strength_spinbox.addStretch()

        layout.addLayout(blur_strength_spinbox)
        
        layout.addStretch()

