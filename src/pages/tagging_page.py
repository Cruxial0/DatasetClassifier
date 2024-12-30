from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QSizePolicy, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTransform, QKeySequence

from src.blur_manager import BlurManager
from src.keybinds.keybind_manager import KeyBinding, KeybindHandler
from src.keybinds.pages.tagging_keybind_page import TaggingKeybindPage
from src.image_handler import ImageHandler
from src.project import Project
from src.button_states import ButtonStateManager
from src.config_handler import ConfigHandler
from src.database.database import Database
from src.update_poller import UpdatePoller
from src.tagging.tag_group import Tag, TagGroup
from src.utils import key_to_unicode
from src.widgets.tag_status_widget import TagStatusWidget

class TaggingPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.button_states: ButtonStateManager = parent.button_states
        self.db: Database = parent.db
        self.update_poller: UpdatePoller = parent.update_poller
        self.config_handler: ConfigHandler = parent.config_handler
        self.active_project: Project = parent.active_project
        self.image_handler: ImageHandler = ImageHandler(self.db, self.config_handler)

        self.page_active = False
        self.image_update_due = False
        self.tag_update_due = False

        self.current_image_id: int = None
        self.current_group: TagGroup = None
        self.active_groups: list[TagGroup] = None
        self.image_tags: list[int] = []

        # Initialize keybind handler
        self.keybind_handler = KeybindHandler(self.config_handler)
        self.keybind_page = TaggingKeybindPage(self)

        self.setupUI()

        self.blur_manager: BlurManager = BlurManager(self.image_label, int(self.config_handler.get_value('privacy.blur_strength')))

        self.load_images()
        self.update_button_colors()

        self.image_tags = self.db.tags.get_image_tags(self.current_image_id)
        self.status_widget.check_group_conditions(self.image_tags)

        # Used in the settings window when updating tags
        self.update_poller.add_method('update_tag_groups', self.update_tag_groups)
        self.update_poller.add_method('update_tagging_images', self.load_images)

        self.keybind_page.register_binding('discard', self.status_widget.prev_button)
        self.keybind_page.register_binding('continue', self.status_widget.next_button)
        self.keybind_page.register_binding('blur', self.blur_manager.toggle_blur)
        self.keybind_handler.register_page("tagging", self.keybind_page)

    def setupUI(self):
        self.main_layout = QHBoxLayout(self)
        self._create_image_viewer()
        self._create_tagging_interface()
        
    def _create_image_viewer(self):
        image_viewer_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)

        nav_button_layout = QHBoxLayout()
        # Remove spacing between buttons
        nav_button_layout.setSpacing(0)
        # Center the buttons in the layout
        nav_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        prev_button = QPushButton('<')
        prev_button.setObjectName("prev_button")
        prev_button.setFixedWidth(40)

        next_button = QPushButton('>')
        next_button.setObjectName("next_button")
        next_button.setFixedWidth(40)

        # Register keybindings
        prev_button.clicked.connect(lambda:self.load_previous_image(absolute=True))
        next_button.clicked.connect(lambda: self.load_next_image(absolute=True))

        nav_button_layout.addWidget(prev_button)
        nav_button_layout.addWidget(next_button)
        
        image_viewer_layout.addWidget(self.image_label)
        image_viewer_layout.addLayout(nav_button_layout)

        self.main_layout.addLayout(image_viewer_layout, 7)

    def _create_tagging_interface(self):
        tagging_layout = QVBoxLayout()

        # Headers
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(7, 0, 7, 0)

        self.status_widget = TagStatusWidget(self)
        self.status_widget.prev_clicked.connect(self.previous_group)
        self.status_widget.next_clicked.connect(self.next_group)
        self.status_widget.latest_clicked.connect(self.to_latest)
        self.status_widget.skip_clicked.connect(self.next_group)
        header_layout.addWidget(self.status_widget)

        # Tags
        self.tags_layout = QVBoxLayout()
        self.tags_layout.setContentsMargins(7, 7, 7, 7)

        self.tag_buttons_layout = QVBoxLayout()
        tag_groups = self.db.tags.get_project_tags(self.active_project.id)
        if tag_groups is not None and len(tag_groups) > 0:
            self.update_tag_groups()
        else:
            add_button = QPushButton("Configure Tag Groups")
            add_button.setStyleSheet(f"background-color: {self.config_handler.get_color('accent_color')}; color: white;")
            add_button.clicked.connect(self.show_configure_tag_groups)
            self.tag_buttons_layout.addWidget(add_button)

        self.tags_layout.addLayout(self.tag_buttons_layout)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(7, 7, 7, 7)
        
        # Progress bar
        progress_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.progress_label = QLabel("0/0")
        self.progress_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
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

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)

        # Ordering
        tagging_layout.addLayout(header_layout)
        tagging_layout.addLayout(self.tags_layout)
        tagging_layout.addStretch(1)
        tagging_layout.addLayout(controls_layout)
        tagging_layout.addLayout(progress_layout)

        self.main_layout.addLayout(tagging_layout, 3)

    def show_configure_tag_groups(self):
        self.parent.open_settings_window(f'tag_groups.{self.current_group.name.replace(" ", "_").replace('.', "_").lower()}')

    def tag_button_click(self, tag_id: int):
        
        if self.current_image_id is None:
            return

        tag_added = False

        if self.db.tags.image_has_tag(self.current_image_id, tag_id):
            self.db.tags.delete_image_tag(self.current_image_id, tag_id)
            tag_added = False
            if tag_id in self.image_tags:
                self.image_tags.remove(tag_id)
        else:
            self.db.tags.add_image_tag(self.current_image_id, tag_id)
            tag_added = True
            if tag_id not in self.image_tags:
                self.image_tags.append(tag_id)
        
        condition_met = self.status_widget.check_group_conditions(self.image_tags)

        # Auto-scroll when TagGroup condition is met (if enabled) (and not overridden by TagGroup)
        if not self.current_group.prevent_auto_scroll:
            if condition_met and self.config_handler.get_value('behaviour.auto_scroll_on_tag_condition') and tag_added:
                self.next_group()

        self.update_button_colors()

    def update_button_colors(self):
        untagged_enabled = self.status_widget.can_add_tag(self.image_tags)
        for i in range(self.tag_buttons_layout.count()):
            if self.tag_buttons_layout is None:
                continue

            layout = self.tag_buttons_layout.itemAt(i).layout()

            if layout is None:
                continue

            first_item = layout.itemAt(1)

            # This means the button does not have a hotkey label
            if first_item is None:
                first_item = layout.itemAt(0)

            btn = first_item.widget()
            if not isinstance(btn, QPushButton):
                continue
            
            # Reset button state
            btn.setEnabled(True)

            tag_id = int(btn.objectName().split('_')[-1])
            
            if self.db.tags.image_has_tag(self.current_image_id, tag_id):
                btn.setStyleSheet(f"background-color: {self.config_handler.get_color('accent_color')}; color: white;")
            elif not untagged_enabled:
                btn.setEnabled(False)
                btn.setStyleSheet(f"background-color: rgb(50, 50, 50); color: rgb(100, 100, 100);")
            else:
                btn.setStyleSheet(f"background-color: {self.config_handler.get_color('background_color')}; color: white;")

    def create_tag_button(self, tag: Tag) -> QHBoxLayout:
        btn_layout = QHBoxLayout()
        
        btn = QPushButton(tag.name)
        btn.setText(tag.name)
        btn.setObjectName(f'tag_button_{tag.id}')
        btn.clicked.connect(lambda: self.tag_button_click(tag.id))
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        if tag.display_order < 10:
            key = f'key_{tag.display_order}'
            hotkey_label = QLabel()
            hotkey_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
            
            btn_layout.addWidget(hotkey_label, 0, Qt.AlignmentFlag.AlignVCenter)
            btn_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignVCenter)

            # Register the button for this key binding
            self.keybind_page.register_binding(key, btn)
            
            # Get and display all key combinations
            bindings = self.keybind_handler.current_bindings.get(key, [])
            shortcuts = []
            for binding in bindings:
                if binding.key is not None:
                    key_sequence = self._create_key_sequence(binding)
                    unicode = key_to_unicode(key_sequence.toString())
                    shortcuts.append(unicode)
            
            shortcut_text = " / ".join(shortcuts) if shortcuts else ""
            hotkey_label.setText(f"({shortcut_text})")
            
            # Store reference to hotkey label for updates
            btn.setProperty("hotkey_label", hotkey_label)
            
            return btn_layout

        btn_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignVCenter)
        return btn_layout

    def update_tag_groups(self, skip_update=False):
        if self.page_active is False:
            self.tag_update_due = True
            return
        
        if not skip_update:
            prev_group_id = 0
            if self.current_group is not None:
                prev_group_id = self.current_group.id
                self.current_group = None

            self.tag_groups = self.db.tags.get_project_tags(self.active_project.id)

            if self.tag_groups is None or len(self.tag_groups) == 0: 
                return
            
            for i in range(len(self.tag_groups)):
                if self.tag_groups[i].id == prev_group_id:
                    self.current_group = self.tag_groups[i]
                    break

            if self.current_group is None:
                self.current_group = self.tag_groups[0]

            self.status_widget.set_tag_groups(self.tag_groups)
        
        if self.current_group.tags is None:
            self.current_group.tags = []
        
        # Unregister all tagging keybinds
        for i in range(10):
            self.keybind_page.remove_keybinding(f'key_{i}')

        # Remove all items in the tags layout
        self._clear_layout(self.tag_buttons_layout)
        
        for tag in self.current_group.tags:
            btn_layout = self.create_tag_button(tag)
            self.tag_buttons_layout.addLayout(btn_layout)

        self.status_widget.set_active_group(self.current_group.order)
        self.status_widget.check_group_conditions(self.image_tags)
        self.update_button_colors()
        self.keybind_handler.register_page("tagging", self.keybind_page)

    def next_group(self):
        if self.tag_groups is None or len(self.tag_groups) < 1 or self.current_group is None:
            return

        if self.current_group.order + 1 >= len(self.tag_groups):
            # check if there are more images
            if not self.load_next_image():
                return
            return
        
        index = self.current_group.order + 1
        self.current_group = self.tag_groups[index]

        self.status_widget.set_prev_button_enabled(True)
        

        self.update_tag_groups(skip_update=True)

        if index == len(self.tag_groups) - 1 and not self.image_handler.next_image_exists():
            self.status_widget.set_next_button_enabled(False)

    def previous_group(self):
        if self.tag_groups is None or len(self.tag_groups) < 1 or self.current_group is None:
            return

        if self.current_group.order - 1 < 0:
            # check if there are more images
            if not self.load_previous_image():
                return
            return
        
        index = self.current_group.order - 1
        self.current_group = self.tag_groups[index]

        if index == 0 and not self.image_handler.previous_image_exists():
            self.status_widget.set_prev_button_enabled(False)

        self.update_tag_groups(skip_update=True)

    def to_latest(self):
        if not self.image_handler.current_image_id:
            return
        
        result = self.db.tags.get_latest_unfinished_image_group(self.active_project.id, self.config_handler.get_value('behaviour.to_latest_strict_mode'))
        if result is None:
            return

        image_id, group_id, group_order = result

        print(f"Unfinished tag group: [{image_id}, {group_id}, {group_order}]")

        if self.image_handler.load_image_from_raw_id(image_id):
            
            self.display_image()

            self.current_group = self.tag_groups[group_order]
            self.image_tags = self.db.tags.get_image_tags(self.current_image_id)
            self.update_tag_groups(skip_update=True)

            condition = self.current_group.order == 0 and not self.image_handler.previous_image_exists()
            self.status_widget.set_prev_button_enabled(not condition)

            self.update_button_colors()
            self.update_progress()

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

        self.current_image_id = self.image_handler.current_image_id

        self.update_score_label()

    def _create_key_sequence(self, binding: KeyBinding) -> QKeySequence:
        """Create a QKeySequence from a KeyBinding"""
        key = binding.key
        if binding.modifiers:
            modifier_str = "+".join(mod.name.replace('KeyboardModifier.', '') 
                                  for mod in binding.modifiers)
            return QKeySequence(f"{modifier_str}+{key}")
        return QKeySequence(key)

    def load_images(self):
        """Load images for the active project"""

        if self.page_active is False:
            self.image_update_due = True
            return

        if self.active_project:
            self.image_handler.load_images(self.active_project.id, get_scored_only=True)
            self.update_progress()
            self.display_image()

    def load_next_image(self, absolute: bool = False) -> bool:
        if self.current_group is None:
            return False
        if self.image_handler.load_next_image():
            self.display_image()

            if not absolute:
                self.current_group = self.tag_groups[0]
                self.image_tags = self.db.tags.get_image_tags(self.current_image_id)
                self.update_tag_groups(skip_update=True)

            self.update_button_colors()
            self.update_progress()
            return True
        return False

    def load_previous_image(self, absolute: bool = False) -> bool:
        if self.current_group is None:
            return False
        if self.image_handler.load_previous_image():
            self.display_image()

            if not absolute:
                self.current_group = self.tag_groups[-1]
                self.image_tags = self.db.tags.get_image_tags(self.current_image_id)
                self.update_tag_groups(skip_update=True)

            self.update_button_colors()
            self.update_progress()
            return True
        return False

    def update_progress(self):
        """Update the progress bar and label"""
        current, total = self.image_handler.get_progress()
        if total > 0:
            self.progress_bar.setValue(current * 100 // total)
            self.progress_label.setText(f"{current}/{total}")

    def update_score_label(self):
        if self.image_handler.current_image_id:
            image_path = self.image_handler.get_current_image_path()
            if image_path:
                current_score, _ = self.image_handler.get_score(image_path)
                self.status_widget.update_score(self.config_handler.get_score(current_score))

    def set_active(self, active: bool = True):
        self.page_active = active

        if active:
            if self.image_update_due:
                self.load_images()
                self.image_tags = self.db.tags.get_image_tags(self.current_image_id)
                self.image_update_due = False
            if self.tag_update_due:
                self.update_tag_groups()
                self.tag_update_due = False

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            
            # Handle nested layouts
            if item.layout():
                self._clear_layout(item.layout())
                
            # Handle widgets
            if item.widget():
                item.widget().deleteLater()
                
            # Delete the item itself
            del item