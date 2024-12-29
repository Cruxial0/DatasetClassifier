from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QTransform, QShortcut, QKeySequence

from src.blur_manager import BlurManager
from src.keybinds.pages.scoring_keybind_page import ScoringKeybindPage
from src.keybinds.keybind_manager import KeyBinding, KeybindHandler
from src.project import Project
from src.config_handler import ConfigHandler
from src.database.database import Database
from src.image_handler import ImageHandler
from src.button_states import ButtonStateManager
from src.ui_components import UIComponents
from src.utils import key_to_unicode
from src.update_poller import UpdatePoller

class ScoringPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.button_states: ButtonStateManager = parent.button_states
        self.db: Database = parent.db
        self.config_handler: ConfigHandler = parent.config_handler
        self.update_poller: UpdatePoller = parent.update_poller
        self.active_project = None
        
        self.image_handler = ImageHandler(self.db, self.config_handler)
        self.default_scores = ['score_0', 'score_1', 'score_2', 'score_3', 'score_4', 'score_5', 'discard']
        self.category_buttons = []
        
        # Initialize keybind handler
        self.keybind_handler = KeybindHandler(self.config_handler)
        self.keybind_page = ScoringKeybindPage(self)
        
        # Initialize UI state variables
        self.alt_pressed = False
        self.ctrl_pressed = False
        
        # Cache for UI updates
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._delayed_ui_update)
        self._pending_updates = set()

        self.setup_ui()

        self.blur_manager: BlurManager = BlurManager(self.image_label, int(self.config_handler.get_value('privacy.blur_strength')))

        self.setup_keybinds()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(self.create_middle_row())
        main_layout.addLayout(self.create_scoring_buttons())

    def setup_keybinds(self):
        # Register score buttons (0-9)
        for i, button in enumerate(self.score_buttons[:-1]):
            self.keybind_page.register_binding(f'key_{i}', lambda s=button.objectName(): self.click_score_button(s))
        
        # Register category buttons with Alt modifier
        for i, (button, _, _) in enumerate(self.category_buttons):
            self.keybind_page.register_binding(f'category_{i}', button)
        
        # Other bindings
        print(f"creating binding for discard button ({self.score_buttons[-1].objectName()})")
        self.keybind_page.register_binding('discard', lambda: self.click_score_button('discard'))
        self.keybind_page.register_binding('next_image', self.next_button)
        self.keybind_page.register_binding('previous_image', self.prev_button)
        self.keybind_page.register_binding('blur', self.toggle_blur)
        
        # Register with handler
        self.keybind_handler.register_page("scoring", self.keybind_page)

    def click_score_button(self, object_name):
        btn = self.findChild(QPushButton, object_name)
        accent_color = self.config_handler.get_color('accent_color')
        
        btn.setStyleSheet(f"background-color: {accent_color};")

        self.score_image(object_name)
        
        if not self.config_handler.get_value('behaviour.auto_scroll_scores'):
            self.update_button_colors()

    def import_categories(self):
        categories = self.db.images.get_unique_categories(self.active_project.id)
        for i, category in enumerate(categories):
            self.add_category_button_from_import(category)

    def update_score_button_labels(self):
        """Update button labels with their keybindings"""
        bindings = self.keybind_handler.current_bindings
        
        # Update score buttons
        for i, button in enumerate(self.score_buttons[:-1]):  # Exclude discard button
            key_bindings = bindings.get(f'key_{i}')
            if key_bindings:
                _, scores = self.config_handler.get_scores()
                # Get shortcuts for both normal and Alt versions
                shortcuts = []
                for binding in key_bindings:
                    key_sequence = self._create_key_sequence(binding)
                    unicode = key_to_unicode(key_sequence.toString())
                    shortcuts.append(unicode)
                
                # Join shortcuts with separator
                shortcut_text = " / ".join(shortcuts)
                score = button.objectName()
                button.setText(f"({shortcut_text})        {scores[score]}")
        
        # Update discard button
        key_bindings = bindings.get('discard')
        if key_bindings:
            discard_button = self.score_buttons[-1]
            shortcuts = []
            for binding in key_bindings:
                key_sequence = self._create_key_sequence(binding)
                unicode = key_to_unicode(key_sequence.toString())
                shortcuts.append(unicode)
            shortcut_text = " / ".join(shortcuts)
            if not f"({shortcut_text})" in discard_button.text():
                discard_button.setText(f"({shortcut_text})        discard")

    def update_category_button_labels(self):
        """Update category button labels with their keybindings"""
        bindings = self.keybind_handler.current_bindings
        
        for i, (button, _, label) in enumerate(self.category_buttons):
            key_bindings = bindings.get(f'category_{i}')
            if key_bindings:
                shortcuts = []
                for binding in key_bindings:
                    key_sequence = self._create_key_sequence(binding)
                    unicode = key_to_unicode(key_sequence.toString())
                    shortcuts.append(unicode)
                shortcut_text = " / ".join(shortcuts)
                label.setText(f"({shortcut_text})")

    def set_active_project(self, project: Project):
        """Update the active project and refresh UI"""
        self.active_project = project
        self.load_images()
        self.display_image()
        self.update_button_colors()
        self.update_progress()
        self.import_categories()

        # Enable relevant UI elements
        self.button_states.toggle_button_group(True, 'score')
        self.button_states.toggle_button_group(True, 'image')
        self.button_states.toggle_button_group(True, 'category')

    def _create_key_sequence(self, binding: KeyBinding) -> QKeySequence:
        """Create a QKeySequence from a KeyBinding"""
        key = binding.key
        if binding.modifiers:
            modifier_str = "+".join(mod.name.replace('KeyboardModifier.', '') 
                                  for mod in binding.modifiers)
            return QKeySequence(f"{modifier_str}+{key}")
        return QKeySequence(key)

    def score_image(self, score: str):
        """Optimized scoring with reduced UI updates"""
        if not self.active_project:
            return

        self.image_handler.score_image(score, None)
        
        # Update UI before loading next image
        # self.update_button_colors()
        
        # Auto-scroll to next image (if enabled)
        if self.config_handler.get_value('behaviour.auto_scroll_scores'):
            if self.image_handler.load_next_image():
                QTimer.singleShot(0, self.display_image)
        
        self.update_poller.poll_update('update_tagging_images')

    def categorize_image(self, category: str):
        if not self.active_project:
            return

        self.image_handler.score_image(None, category)
        
        # Update UI before loading next image
        self.update_button_colors()

    def load_next_image(self):
        if self.image_handler.load_next_image():
            self.display_image()

    def load_previous_image(self):
        if self.image_handler.load_previous_image():
            self.display_image()

    def load_latest_image(self):
        """Load the latest scored image in the project"""
        latest_id = self.db.images.get_latest_image_id(self.active_project.id)
        if latest_id is not None and self.image_handler.image_ids:
            # Find the index of the latest image ID in our list
            try:
                latest_index = self.image_handler.image_ids.index(latest_id)
                self.image_handler.set_index(latest_index)
                self.display_image()
                
                # Update navigation button states
                self.button_states.toggle_button(False, 'to_latest_button_right', 'image')
                self.button_states.toggle_button(False, 'to_latest_button_left', 'image')
            except ValueError:
                print(f"Latest image ID {latest_id} not found in current image list")

    def display_image(self):
        """Optimized image display"""
        pixmap = self.image_handler.get_current_image()
        if not pixmap:
            return

        # Cache the orientation for the current image
        if not hasattr(self, '_cached_orientation'):
            self._cached_orientation = {}
            
        image_id = self.image_handler.current_image_id
        if image_id not in self._cached_orientation:
            self._cached_orientation[image_id] = self.image_handler.get_orientation()

        orientation = self._cached_orientation[image_id]
        
        # Only create transform if needed
        transform = None
        if orientation != "Normal":
            transform = QTransform()
            rotations = {
                "Rotate 90 CW": 90,
                "Rotate 180": 180,
                "Rotate 270 CW": 270,
                "Rotate 90 CCW": 270
            }
            if orientation in rotations:
                transform.rotate(rotations[orientation])
        
        # Apply transform if needed
        if transform:
            pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        
        # Scale and display
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
        # Schedule UI updates
        self.schedule_ui_update('progress')
        self.schedule_ui_update('buttons')
        self.schedule_ui_update('latest')

        # self.update_button_colors()
    
    def load_images(self):
        """Load images for the active project"""
        if self.active_project:
            self.image_handler.load_images(self.active_project.id, False)
            self.update_progress()
            self.display_image()

    def update_progress(self):
        """Update the progress bar and label"""
        current, total = self.image_handler.get_progress()
        if total > 0:
            self.progress_bar.setValue(current * 100 // total)
            self.progress_label.setText(f"{current}/{total}")

    
    def manage_latest_button_state(self):
        """Update the state of Latest Image navigation buttons"""
        if not self.db or not self.active_project:
            return

        latest_id = self.db.images.get_latest_image_id(self.active_project.id)
        if latest_id is None or not self.image_handler.current_image_id:
            return

        # Get indices for comparison
        try:
            latest_index = self.image_handler.image_ids.index(latest_id)
            current_index = self.image_handler.image_ids.index(self.image_handler.current_image_id)
            
            # Update button states based on position
            if current_index == latest_index:
                self.button_states.toggle_button(False, 'to_latest_button_right', 'image')
                self.button_states.toggle_button(False, 'to_latest_button_left', 'image')
            elif current_index > latest_index:
                self.button_states.toggle_button(True, 'to_latest_button_left', 'image')
                self.button_states.toggle_button(False, 'to_latest_button_right', 'image')
            else:
                self.button_states.toggle_button(True, 'to_latest_button_right', 'image')
                self.button_states.toggle_button(False, 'to_latest_button_left', 'image')
        except ValueError:
            if not self.db.projects.has_scores(self.active_project.id):
                return
            
            print("Error: Could not determine image positions")

    def create_middle_row(self):
        layout = QHBoxLayout()
        
        image_viewer_layout, self.prev_button, self.image_label, self.next_button, self.to_latest_button_right, self.to_latest_button_left = UIComponents.create_image_viewer(self.button_states.image_enabled)
        layout.addLayout(image_viewer_layout, 7)

        self.prev_button.clicked.connect(self.load_previous_image)
        self.next_button.clicked.connect(self.load_next_image)
        self.to_latest_button_right.clicked.connect(self.load_latest_image)
        self.to_latest_button_left.clicked.connect(self.load_latest_image)

        category_buttons_layout, self.category_input, self.category_add_button, self.category_button_layout = UIComponents.create_category_buttons(self.button_states.category_enabled)
        layout.addLayout(category_buttons_layout, 3)

        self.category_input.textChanged.connect(self.check_category_button_name)
        self.category_add_button.clicked.connect(self.add_category_button)

        self.button_states.declare_button_group([self.prev_button, self.next_button, self.to_latest_button_right, self.to_latest_button_left], 'image')
        self.button_states.declare_button_group([self.category_input, self.category_add_button], 'category')

        return layout
    
    def create_scoring_buttons(self):
        layout, self.score_buttons, self.progress_bar, self.progress_label = UIComponents.create_scoring_buttons(self.default_scores, self.button_states.score_enabled, self.config_handler)
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid transparent;
                border-radius: 5px;
                text-align: center;
            }}

            QProgressBar::chunk {{
                background-color: {self.config_handler.get_color('accent_color')};
                border-radius: 5px;
            }}
            """)
        self.button_states.declare_button_group(self.score_buttons, 'score')
        self.score_layout = layout.itemAt(0).layout()  # Store the score_layout
        
        return layout

    def check_category_button_name(self):
        name = self.category_input.text()
        if name and any(button[0].text() == name for button in self.category_buttons):
            self.category_add_button.setStyleSheet(f"background-color: {self.config_handler.get_color('warning_color')}; color: white;")
        else:
            self.category_add_button.setStyleSheet(f"background-color: {self.config_handler.get_color('accent_color')}; color: white;")

    def add_category_button_from_import(self, name: str):
        self._create_category_button(name)
        self.update_category_button_labels()

    def add_category_button(self):
        """Add a new category button with keybinding support"""
        if len(self.category_buttons) < 10:
            name = self.category_input.text()
            if name and not any(button[0].text() == name for button in self.category_buttons):
                self._create_category_button(name)
                self.category_input.clear()
                self.update_category_button_labels()

    def _create_category_button(self, name: str):
        button = QPushButton(name)
        button.clicked.connect(lambda _, s=name: self.categorize_image(s))
        remove_button = QPushButton("-")
        remove_button.setMaximumWidth(30)
        remove_button.clicked.connect(lambda _, b=button: self.remove_category_button(b))
        
        # Add keybinding label
        keybind_label = QLabel()
        keybind_label.setAlignment(Qt.AlignmentFlag.AlignRight | 
                                    Qt.AlignmentFlag.AlignVCenter)
        keybind_label.setFixedWidth(40)
        keybind_label.setStyleSheet("min-width: 40px; max-width: 40px;")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(keybind_label)
        button_layout.addWidget(button)
        button_layout.addWidget(remove_button)
        
        self.category_button_layout.addLayout(button_layout)
        self.category_buttons.append((button, remove_button, keybind_label))
        
            # Register keybinding immediately after creating the button
        category_index = len(self.category_buttons) - 1
        self.keybind_page.register_binding(f'category_{category_index}', button)
        
        # Update keybinding in the handler to apply it
        self.keybind_handler.update_keybinding(
            f'category_{category_index}',
            [KeyBinding(str(category_index), [Qt.KeyboardModifier.AltModifier])]
        )

    def remove_category_button(self, button):
        """Remove a category button and its keybinding"""
        for i, (btn, remove_btn, label) in enumerate(self.category_buttons):
            if btn == button:
                # Remove keybinding
                self.keybind_page.remove_keybinding(f'category_{i}')
                
                # Remove UI elements
                btn.deleteLater()
                remove_btn.deleteLater()
                label.deleteLater()
                layout = btn.parent().layout()
                if layout:
                    layout.deleteLater()
                
                self.category_buttons.pop(i)
                
                # Re-register remaining category buttons with updated indices
                self._reindex_category_bindings()
                break

    def _reindex_category_bindings(self):
        """Update category button indices after removal"""
        for i, (button, _, _) in enumerate(self.category_buttons):
            self.keybind_page.remove_keybinding(f'category_{i}')
            self.keybind_page.register_binding(f'category_{i}', button)
        self.update_category_button_labels()

    def update_button_colors(self):
        """
        Update score button colors based on the current image's score.

        If the current image has a score, change the corresponding button's color to the accent color.
        If the current image does not have a score, change the 'discard' button's color to the alternate color.
        If the current image does not have a score and the 'discard' button does not exist, do not change any button colors.

        This function is optimized to use a cache of stylesheet strings to avoid redundant computation.
        """

        if not self.db or not self.image_handler.current_image_id:
            return

        current_image = self.image_handler.get_current_image_path()
        if not current_image:
            return
        
        # Get score from optimized cache
        current_score, current_categories = self.image_handler.get_score(current_image)
        
        # Update score buttons
        style_cache = {}  # Cache stylesheet strings
        
        for i in range(self.score_layout.count()):
            button = self.score_layout.itemAt(i).widget()
            if not isinstance(button, QPushButton) or not button.isEnabled():
                continue

            style_key = (button.objectName() == current_score, button.objectName() == 'discard')
            if style_key not in style_cache:
                if button.objectName() == current_score:
                    color = self.config_handler.get_color('warning_color' if button.objectName() == 'discard' else 'accent_color')
                    style_cache[style_key] = f"background-color: {color}; color: white;"
                else:
                    color = self.config_handler.get_color('alternate_color') if button.objectName() == 'discard' else ""
                    style_cache[style_key] = f"background-color: {color}; color: white;" if color else ""
            
            button.setStyleSheet(style_cache[style_key])

        # Update category buttons
        for i in range(self.category_button_layout.count()):
            button = self.category_button_layout.itemAt(i).layout().itemAt(1).widget()
            if not isinstance(button, QPushButton) or not button.isEnabled():
                continue

            if button.text() in current_categories:
                button.setStyleSheet(f"background-color: {self.config_handler.get_color('warning_color')}; color: white;")
            else:
                button.setStyleSheet(f"background-color: {self.config_handler.get_color('alternate_color')}; color: white;")

    def schedule_ui_update(self, update_type):
        """Schedule a UI update to batch multiple updates together"""
        self._pending_updates.add(update_type)
        self._update_timer.start(50)  # 50ms delay

    def _delayed_ui_update(self):
        """Process all pending UI updates at once"""
        if 'progress' in self._pending_updates:
            self.update_progress()
        if 'buttons' in self._pending_updates:
            self.update_button_colors()
        if 'latest' in self._pending_updates:
            self.manage_latest_button_state()
        self._pending_updates.clear()

    def toggle_blur(self):
        self.blur_manager.toggle_blur()