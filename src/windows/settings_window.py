import random
import string
import sys
from typing import Literal
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QCheckBox, QPushButton, 
                            QStackedWidget, QComboBox, QColorDialog, QSpinBox)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal
from PyQt6.QtGui import QColor, QKeySequence
from src.database.database import Database
from src.project import Project
from src.score_presets import get_preset, get_preset_list
from src.config_handler import ConfigHandler
from src.windows.settings_pages.tag_groups_settings import TagGroupsSettings
from src.update_poller import UpdatePoller

class ColorButton(QPushButton):
    def __init__(self, color=QColor, parent=None):  # Add parent parameter
        super().__init__(parent)  # Pass parent to superclass
        
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
        
        self.db = parent.db
        self.project = parent.active_project
        self.update_poller = parent.update_poller
        self.config_handler = parent.config_handler
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create navigation bar
        nav_widget = QWidget()
        nav_widget.setFixedWidth(200)
        nav_layout = QVBoxLayout(nav_widget)
        
        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        
        # Initialize pages dict but don't create pages yet
        self._pages = {}
        self._page_creators = {
            "behaviour": self.create_behaviour_page,
            "export": self.create_export_page,
            "keybinds": self.create_keybinds_page,
            "colors": self.create_colors_page,
            "scoring": self.create_scoring_page,
            "privacy": self.create_privacy_page,
            "tag_groups": lambda: TagGroupsSettings(self)
        }
        
        # Add navigation buttons
        for name in self._page_creators.keys():
            btn = QPushButton(name.replace('_', ' ').title())
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        # Add widgets to main layout
        layout.addWidget(nav_widget)
        layout.addWidget(self.content_stack)
        
        if page:
            self.navigate_path(page)
            return

        # Select first page by default
        first_button = nav_widget.findChild(QPushButton)
        if first_button:
            first_button.setChecked(True)
            self.switch_page(list(self._page_creators.keys())[0])

    def navigate_path(self, path: str):
        """Navigate to a path in the settings window based on dot notation"""
        page = path.split('.')[0]
        self.switch_page(page)

        if page in ['tag_groups']:
            self._pages[page].navigate_path(".".join(path.split('.')[1:]))

    def get_page(self, page_name: str):
        """Get or create a page"""
        if page_name not in self._pages:
            creator = self._page_creators.get(page_name)
            if creator:
                self._pages[page_name] = creator()
                self.content_stack.addWidget(self._pages[page_name])
        return self._pages.get(page_name)

    def switch_page(self, page_name: str):
        # convert page_name to snake_case
        page_name = page_name.replace(' ', '_').lower()
        
        # Uncheck all buttons except the clicked one
        nav_buttons = self.findChildren(QPushButton)
        for button in nav_buttons:
            if button.text().replace(' ', '_').lower() == page_name:
                button.setChecked(True)
            else:
                button.setChecked(False)
        
        # Get or create the page and switch to it
        page = self.get_page(page_name)
        if page:
            self.content_stack.setCurrentWidget(page)

    def bind_callback(self, callback, callback_type: Literal['scoring', 'colors', 'keybinds']):
        if callback_type == 'scoring':
            self.scoring_updated_callback = callback
        elif callback_type == 'colors':
            self.colors_updated_callback = callback
        elif callback_type == 'keybinds':
            self.keybinds_updated_callback = callback

    def create_behaviour_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        auto_scroll_scores = QCheckBox("Auto scroll on scoring")
        auto_scroll_scores.setToolTip("Automatically moves to the next image when a score button is clicked")
        auto_scroll_scores.setChecked(self.config.get_value('behaviour.auto_scroll_scores'))
        auto_scroll_scores.checkStateChanged.connect(lambda state: self.config.set_value('behaviour.auto_scroll_scores', state.value > 0))

        auto_scroll_on_tag_condition = QCheckBox("Auto scroll when TagGroup condition is met")
        auto_scroll_on_tag_condition.setToolTip("Automatically moves to the next TagGroup when a TagGroup condition is met")
        auto_scroll_on_tag_condition.setChecked(self.config.get_value('behaviour.auto_scroll_on_tag_condition'))
        auto_scroll_on_tag_condition.checkStateChanged.connect(lambda state: self.config.set_value('behaviour.auto_scroll_on_tag_condition', state.value > 0))

        layout.addWidget(auto_scroll_scores)
        layout.addWidget(auto_scroll_on_tag_condition)

        layout.addStretch()
        return page

    def create_export_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        export_caption = QCheckBox("Export captions")
        seperate_by_score = QCheckBox("Seperate by score")
        delete_images = QCheckBox("Delete images from source directory")
        
        caption_format_layout = QHBoxLayout()
        caption_format_layout.addWidget(QLabel("Export format:"))
        caption_format = QComboBox()
        caption_format.addItems(['.txt', '.caption'])
        caption_format.setCurrentText(self.config.get_value('export_options.caption_format'))
        caption_format_layout.addWidget(caption_format)

        export_caption.setChecked(self.config.get_export_option('export_captions'))
        seperate_by_score.setChecked(self.config.get_export_option('seperate_by_score'))
        delete_images.setChecked(self.config.get_export_option('delete_images'))

        export_caption.checkStateChanged.connect(lambda state: self.update_export_option((state.value > 0), 'export_captions'))
        caption_format.currentTextChanged.connect(lambda text: self.update_export_option(text, 'caption_format'))
        seperate_by_score.checkStateChanged.connect(lambda state: self.update_export_option((state.value > 0), 'seperate_by_score'))
        delete_images.checkStateChanged.connect(lambda state: self.update_export_option((state.value > 0), 'delete_images'))

        layout.addWidget(export_caption)
        layout.addLayout(caption_format_layout)
        layout.addWidget(seperate_by_score)
        layout.addWidget(delete_images)
        layout.addStretch()
        return page

    def update_export_option(self, value, key):
        self.config.set_value(f'export_options.{key}', value)
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
            "Continue": loaded_keybinds['continue'],
            "Discard": loaded_keybinds['discard'], 
            "Next Image": loaded_keybinds['next_image'], 
            "Previous Image": loaded_keybinds['previous_image'],
            "Blur": loaded_keybinds['blur']
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
        for row in self._pages["keybinds"].findChildren(QHBoxLayout):
            label = row.itemAt(0).widget()
            if label.text() == key_name:
                keybind_widget = row.itemAt(1).widget()
                keybind_widget.key = key
                keybind_widget.setText(keybind_widget.get_key_name(key))

    def create_colors_page(self):
        if hasattr(self, '_colors_page'):
            return self._colors_page
            
        self._colors_page = QWidget(self)
        layout = QVBoxLayout(self._colors_page)
        
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
            label = QLabel(name, self._colors_page)
            label.setFixedWidth(100)
            color_button = ColorButton(color, self._colors_page)
            color_button.clicked.connect(lambda _, cb=color_button, n=self.get_key_name(name): 
                cb.chooseColor(n, self.config, self.colors_updated_callback))
            row.addWidget(label)
            row.addWidget(color_button)
            row.addStretch()
            layout.addLayout(row)

        layout.addStretch(1)
        return self._colors_page

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
    
    def create_privacy_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Create a row with a label and a SpinBox
        row = QHBoxLayout()
        label = QLabel("Blur Strength")
        label.setFixedWidth(100)

        blur_strength = QSpinBox()
        blur_strength.setRange(0, 100)
        blur_strength.setValue(self.config.get_value('privacy.blur_strength'))
        blur_strength.setFixedWidth(100)

        info_label = QLabel("(0-100) (requires restart)")
        info_label.setFixedWidth(150)

        row.addWidget(label)
        row.addWidget(blur_strength)
        row.addWidget(info_label)
        row.addStretch() 
        layout.addLayout(row)
    
        def update_blur_strength(value):
            self.config.set_value('privacy.blur_strength', value)
            self.config.save_config()

        blur_strength.valueChanged.connect(update_blur_strength)
        
        layout.addStretch()
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