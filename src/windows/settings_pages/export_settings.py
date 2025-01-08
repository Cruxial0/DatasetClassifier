
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox
from src.windows.settings_pages.settings_widget import SettingsWidget


class ExportSettingsPage(SettingsWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        caption_combo = self._create_combobox("Caption format:", ['.txt', '.caption'], 'export_options.caption_format')
        caption_combo.addStretch(1)

        layout.addLayout(self._create_header("Captions"))
        layout.addLayout(self._create_checkbox("Export captions", "Whether or not to export captions", "export_options.export_captions"))
        layout.addLayout(caption_combo)
        layout.addLayout(self._create_header("Categorization", category_break=True))
        layout.addLayout(self._create_checkbox("Seperate by score", "Whether or not to seperate image exports into directories by score", "export_options.seperate_by_score"))
        layout.addLayout(self._create_checkbox("Delete images from source directory", "Whether or not to delete images from source directory", "export_options.delete_images"))
        layout.addStretch()