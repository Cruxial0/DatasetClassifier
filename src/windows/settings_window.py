import random
import string
import sys
from typing import Literal
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QCheckBox, QPushButton, 
                            QStackedWidget, QComboBox, QColorDialog)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal
from PyQt6.QtGui import QColor, QKeySequence
from src.database.database import Database
from src.project import Project
from src.score_presets import get_preset, get_preset_list
from src.config_handler import ConfigHandler
from src.windows.settings_pages.tag_groups_settings import TagGroupsSettings
from src.update_poller import UpdatePoller

class ColorButton(QPushButton):
    def __init__(self, color=QColor):
        super().__init__()
        alphabet = string.ascii_lowercase + string.digits
        self.name = ''.join(random.choices(alphabet, k=8))
        self.setObjectName(self.name)
        self.color = color
        self.setFixedSize(50, 30)
        self.updateStyle()

    def updateStyle(self):
        self.setStyleSheet(
            f"#{self.name} {{ background-color: {self.color.name()}; }}"
        )

    def chooseColor(self, color_name: str, config: ConfigHandler, callback):
        dialog = QColorDialog(self.color, self)
        if dialog.exec() == QColorDialog.DialogCode.Accepted:
            self.color = dialog.currentColor()
            self.updateStyle()

            hex_color = dialog.currentColor().name()
            config.set_color(color_name, hex_color)
            config.save_config()
            
            if callback:
                callback()

class KeybindWidget(QPushButton):
    keyPressed = pyqtSignal(int)

    def __init__(self, key=0, parent=None):
        super().__init__(parent)
        self.key = key
        self.setText(self.get_key_name(key) or "Press a key")
        self.setCheckable(True)
        self.clicked.connect(self.start_capture)
        self.installEventFilter(self)
        self.is_capturing = False

    def get_key_name(self, keycode):
        if keycode == 0:
            return "None"
        return QKeySequence(keycode).toString()

    def eventFilter(self, obj, event):
        if self.is_capturing and event.type() == QEvent.Type.KeyPress:
            self.key = event.key()
            self.setText(self.get_key_name(self.key))
            self.setChecked(False)
            self.is_capturing = False
            self.keyPressed.emit(self.key)
            return True
        return super().eventFilter(obj, event)

    def start_capture(self):
        self.setChecked(True)
        self.is_capturing = True

class SettingsWindow(QMainWindow):
    def __init__(self, config: ConfigHandler, parent, page: str = None):
        super().__init__()

        self.scoring_updated_callback = None
        self.colors_updated_callback = None
        self.keybinds_updated_callback = None

        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 600)
        
        self.db: Database = parent.db
        self.project: Database = parent.active_project
        self.update_poller: UpdatePoller = parent.update_poller
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create navigation bar
        nav_widget = QWidget()
        nav_widget.setFixedWidth(200)
        # nav_widget.setStyleSheet("background-color: #f0f0f0;")
        nav_layout = QVBoxLayout(nav_widget)
        
        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        
        # Add navigation buttons and corresponding pages
        self.pages = {
            "Export": self.create_export_page(),
            "Keybinds": self.create_keybinds_page(),
            "Colors": self.create_colors_page(),
            "Scoring": self.create_scoring_page(),
            "Tag Groups": TagGroupsSettings(self)
        }
        
        for name, page in self.pages.items():
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))
            nav_layout.addWidget(btn)
            self.content_stack.addWidget(page)
        
        nav_layout.addStretch()
        
        # Add widgets to main layout
        layout.addWidget(nav_widget)
        layout.addWidget(self.content_stack)
        
        # Select first page by default
        first_button = nav_widget.findChild(QPushButton)
        if first_button:
            first_button.setChecked(True)

    def bind_callback(self, callback, callback_type: Literal['scoring', 'colors', 'keybinds']):
        if callback_type == 'scoring':
            self.scoring_updated_callback = callback
        elif callback_type == 'colors':
            self.colors_updated_callback = callback
        elif callback_type == 'keybinds':
            self.keybinds_updated_callback = callback

    def switch_page(self, page_name):
        # Uncheck all buttons except the clicked one
        nav_buttons = self.findChildren(QPushButton)
        for button in nav_buttons:
            if button.text() == page_name:
                button.setChecked(True)
            else:
                button.setChecked(False)
        
        # Switch to the selected page
        self.content_stack.setCurrentWidget(self.pages[page_name])

    def create_export_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        export_caption = QCheckBox("Export captions")
        seperate_by_score = QCheckBox("Seperate by score")
        delete_images = QCheckBox("Delete images from source directory")
        
        export_caption.setChecked(self.config.get_export_option('export_captions'))
        seperate_by_score.setChecked(self.config.get_export_option('seperate_by_score'))
        delete_images.setChecked(self.config.get_export_option('delete_images'))

        export_caption.stateChanged.connect(lambda state: self.update_export_option(state, 'export_captions'))
        seperate_by_score.stateChanged.connect(lambda state: self.update_export_option(state, 'seperate_by_score'))
        delete_images.stateChanged.connect(lambda state: self.update_export_option(state, 'delete_images'))

        layout.addWidget(export_caption)
        layout.addWidget(seperate_by_score)
        layout.addWidget(delete_images)
        layout.addStretch()
        return page

    def update_export_option(self, state, key):
        if state == Qt.CheckState.Checked.value:
            self.config.set_export_option(key, True)
        elif state == Qt.CheckState.Unchecked.value:
            self.config.set_export_option(key, False)
        
        self.config.save_config()

    def create_keybinds_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        loaded_keybinds = self.config.get_keybindings()
        keybinds = {
            "Key 1": loaded_keybinds['key_0'], 
            "Key 2": loaded_keybinds['key_1'], 
            "Key 3": loaded_keybinds['key_2'], 
            "Key 4": loaded_keybinds['key_3'], 
            "Key 5": loaded_keybinds['key_4'],
            "Key 6": loaded_keybinds['key_5'], 
            "Key 7": loaded_keybinds['key_6'], 
            "Key 8": loaded_keybinds['key_7'], 
            "Key 9": loaded_keybinds['key_8'], 
            "Key 10": loaded_keybinds['key_9'],
            "Discard": loaded_keybinds['discard'], 
            "Next Image": loaded_keybinds['image_next'], 
            "Previous Image": loaded_keybinds['image_previous']
        }
        
        for key, value in keybinds.items():
            row = QHBoxLayout()
            label = QLabel(key)
            label.setFixedWidth(100)
            keybind_widget = KeybindWidget(value)
            keybind_widget.keyPressed.connect(lambda k, k_name=self.get_key_name(key): self.update_keybind(k_name, k))
            row.addWidget(label)
            row.addWidget(keybind_widget)
            layout.addLayout(row)
        
        layout.addStretch()
        return page

    def get_key_name(self, key: str):
        formatted = key.lower().replace(' ', '_')
        if formatted.startswith('key_'):
            index = int(formatted.split('_')[1]) - 1
            return f"key_{index}"
        return formatted

    def update_keybind(self, key_name, key):
        # Update the keybindings in the config handler
        self.config.set_keybind(key_name, key)
        self.config.save_config()
        if self.keybinds_updated_callback:
            self.keybinds_updated_callback()

        # Update the UI
        for row in self.pages["Keybinds"].findChildren(QHBoxLayout):
            label = row.itemAt(0).widget()
            if label.text() == key_name:
                keybind_widget = row.itemAt(1).widget()
                keybind_widget.key = key
                keybind_widget.setText(keybind_widget.get_key_name(key))

    def create_colors_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        loaded_colors = self.config.get_colors()
        colors = {
            "Accent Color": QColor.fromString(loaded_colors['accent_color']),
            "Add Color": QColor.fromString(loaded_colors['add_color']),
            "Alternate Color": QColor.fromString(loaded_colors['alternate_color']),
            "Select Color": QColor.fromString(loaded_colors['select_color']),
            "Warning Color": QColor.fromString(loaded_colors['warning_color'])
        }
        
        for name, color in colors.items():
            row = QHBoxLayout()
            label = QLabel(name)
            label.setFixedWidth(100)
            color_button = ColorButton(color)
            color_button.clicked.connect(lambda _, cb=color_button, n=self.get_key_name(name): cb.chooseColor(n, self.config, self.colors_updated_callback))
            row.addWidget(label)
            row.addWidget(color_button)
            row.addStretch()
            layout.addLayout(row)
        
        layout.addStretch()
        return page

    def create_scoring_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Create the row with a label and combo box
        row = QHBoxLayout()
        label = QLabel("Scoring Preset")
        label.setFixedWidth(100)
        preset_combo = QComboBox()
        preset_combo.addItems(get_preset_list())

        selected_preset = self.config.get_selected_preset()
        if selected_preset in get_preset_list():
            preset_combo.setCurrentText(selected_preset)
            

        row.addWidget(label)
        row.addWidget(preset_combo)
        layout.addLayout(row)
        
        # Create the buttons and store them for later updates
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
        
        layout.addLayout(buttons_layout)
        layout.addStretch()

        self.update_button_names(preset_combo.currentText())

        # Connect combo box signal to update button names
        preset_combo.currentTextChanged.connect(lambda text: self.update_button_names(text, True))
        
        return page

    def update_button_names(self, preset_name, save=False):
        preset, scores = get_preset(preset_name)
        for i, button in enumerate(self.buttons):
            button.setText(scores[i])
        
        if save:
            self.config.set_scores_preset(preset)
            self.config.save_config()
            if self.scoring_updated_callback:
                self.scoring_updated_callback()