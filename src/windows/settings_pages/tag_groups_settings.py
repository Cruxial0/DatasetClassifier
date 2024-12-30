from typing import Callable, Literal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QLineEdit, QMessageBox, QCheckBox, QSpinBox, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.config_handler import ConfigHandler
from src.project import Project
from src.database.database import Database
from src.tagging.tag_group import Tag, TagGroup
from src.update_poller import UpdatePoller

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QPalette

from src.windows.settings_pages.settings_widget import SettingsWidget

class TagWidget(QWidget):
    def __init__(self, tag: Tag, database: Database, update_poller: UpdatePoller, delete_callback: Callable, parent=None):
        super().__init__(parent)
        self.tag: Tag = tag
        self.db: Database = database
        self.update_poller: UpdatePoller = update_poller
        self.delete_callback = delete_callback
        
        # Create timer for debouncing
        self.write_timer = QTimer()
        self.write_timer.setSingleShot(True)  # Timer will only fire once
        self.write_timer.setInterval(500)  # 500ms delay
        self.write_timer.timeout.connect(self._write_tag_to_db)  # Connect to actual database write
        
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout(self)

        self.line_edit = QLineEdit()
        self.line_edit.setText(self.tag.name)
        self.line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.line_edit.textChanged.connect(self.write_tag)

        remove_button = QPushButton("-")
        remove_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        remove_button.clicked.connect(self.delete_tag)
        
        self.main_layout.addWidget(self.line_edit)
        self.main_layout.addWidget(remove_button)

    def write_tag(self):
        # Reset and start timer
        self.write_timer.stop()  # Stop any existing timer
        self.write_timer.start()  # Start the timer again
        
    def _write_tag_to_db(self):
        # This is called after the timer expires
        self.tag.name = self.line_edit.text()
        self.db.tags.update_tag(self.tag)

        # Used to update the UI in the Tagging Page
        self.update_poller.poll_update('update_tag_groups')

    def delete_tag(self):
        self.delete_callback(self.tag.id, 'tag')
        self.db.tags.delete_tag(self.tag.id)

class TagListItem(QListWidgetItem):
    def __init__(self, tag: Tag, database: Database, update_poller: UpdatePoller, delete_callback: Callable, list_widget: QListWidget):
        super().__init__(list_widget)
        self.tag = tag

        widget = TagWidget(tag=tag, database=database, update_poller=update_poller, delete_callback=delete_callback)

        list_widget.setItemWidget(self, widget)

        self.setSizeHint(widget.sizeHint())

class TagGroupWidget(QWidget):
    clicked = pyqtSignal(TagGroup)
    
    def __init__(self, tag_group: TagGroup, database: Database, update_poller: UpdatePoller, delete_callback: Callable, config_handler: ConfigHandler, parent=None):
        super().__init__(parent)
        self.tag_group = tag_group
        self.db: Database = database
        self.update_poller: UpdatePoller = update_poller
        self.delete_callback = delete_callback
        self.config_handler = config_handler
        self.is_selected = False
        
        # Create a frame to handle the selection highlighting
        self.frame = QFrame(self)
        self.frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)
        
        self.init_palette()
        self.initUI()
        
    def init_palette(self):
        # Create base palette
        self.base_palette = QPalette()
        self.base_palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.transparent)
        self.base_palette.setColor(QPalette.ColorRole.WindowText, self.palette().text().color())
        
        # Create highlight palette
        self.highlight_palette = QPalette()
        accent_color = QColor(self.config_handler.get_color('accent_color'))
        self.highlight_palette.setColor(QPalette.ColorRole.Window, accent_color)
        self.highlight_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)

    def initUI(self):
        # Main layout for the widget
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.frame)
        
        # Layout for the frame content
        self.main_layout = QHBoxLayout(self.frame)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create and configure name label
        self.name_label = QLabel(self.tag_group.name)
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Create and configure delete button
        delete_button = QPushButton("-")
        delete_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        delete_button.setFixedWidth(30)
        delete_button.clicked.connect(self.delete_tag_group)
        
        # Add widgets to layout
        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(delete_button)
        
        # Set cursor style
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Initialize style
        self.setSelected(False)
    
    def setSelected(self, selected: bool):
        self.is_selected = selected
        
        # Apply the appropriate style
        if selected:
            self.frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.config_handler.get_color('accent_color')};
                    border: none;
                }}
            """)
            self.name_label.setStyleSheet("color: white;")
        else:
            self.frame.setStyleSheet("")
            self.name_label.setStyleSheet("")
        
        # Force update
        self.update()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.tag_group)
        super().mousePressEvent(event)
    
    def delete_tag_group(self):
        result = QMessageBox.question(
            self, 
            "Delete Tag Group", 
            "Are you sure you want to delete this tag group?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if result == QMessageBox.StandardButton.Yes:
            self.delete_callback(self.tag_group.id, 'tag_group')
            self.db.tags.delete_tag_group(self.tag_group.id)

class TagGroupListItem(QListWidgetItem):
    def __init__(self, tag_group: TagGroup, database: Database, update_poller: UpdatePoller, delete_callback: Callable, list_widget: QListWidget, config_handler: ConfigHandler, callback: Callable):
        super().__init__(list_widget)
        self.tag_group = tag_group
        
        # Create the widget that will be displayed in the list item
        self.widget = TagGroupWidget(
            tag_group=tag_group,
            database=database,
            delete_callback=delete_callback,
            update_poller=update_poller,
            config_handler=config_handler
        )
        
        # Connect the widget's clicked signal to the callback
        self.widget.clicked.connect(callback)
        
        # Set the widget for this list item
        list_widget.setItemWidget(self, self.widget)
        
        # Set an appropriate size for the item
        self.setSizeHint(self.widget.sizeHint())
        
    def setSelected(self, selected: bool):
        print(f"TagGroupListItem setSelected {selected} ({self.tag_group.name})")
        super().setSelected(selected)
        self.widget.setSelected(selected)


class TagGroupEditWidget(QWidget):
    group_updated: pyqtSignal = pyqtSignal(TagGroup)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.active_group = None
        self.is_scripted = False

        self.main_layout = QVBoxLayout(self)

        self.group_label = QLabel("Editing:")
        self.group_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        name_edit_layout = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_save_button = QPushButton("Save")

        name_edit_layout.addWidget(self.name_edit)
        name_edit_layout.addWidget(self.name_save_button)
    
        self.is_required_toggle = QCheckBox("Required")
        self.is_required_toggle.setToolTip("Whether or not the condition for this TagGroup must be met to proceed")

        min_tags_layout = QHBoxLayout()
        self.min_tags_label = QLabel("Minimum Tags")
        self.min_tags_input = QSpinBox()
        self.allow_multiple_toggle = QCheckBox("Allow Multiple")

        self.min_tags_label.setToolTip("Minimum number of tags required to proceed\nDoes not apply if 'Allow Multiple' is unchecked")
        self.allow_multiple_toggle.setToolTip("Whether or not multiple tags can be selected for this TagGroup")

        self.min_tags_input.setMinimum(1)

        self.prevent_auto_scroll = QCheckBox("Prevent Auto Scroll")
        self.prevent_auto_scroll.setToolTip("Prevents auto scrolling when a TagGroup condition is met")

        min_tags_layout.addWidget(self.min_tags_label)
        min_tags_layout.addWidget(self.min_tags_input)
        min_tags_layout.addWidget(self.allow_multiple_toggle)

        self.main_layout.addWidget(self.group_label)
        self.main_layout.addLayout(name_edit_layout)
        self.main_layout.addWidget(self.is_required_toggle)
        self.main_layout.addLayout(min_tags_layout)
        self.main_layout.addWidget(self.prevent_auto_scroll)

        for control in [self.name_edit, self.name_save_button, self.min_tags_label, self.min_tags_input, self.allow_multiple_toggle, self.is_required_toggle, self.prevent_auto_scroll]:
            control.setEnabled(False)

        # Bind signals
        self.name_edit.textChanged.connect(self.on_name_edit_changed)
        self.name_save_button.clicked.connect(self.on_name_edit_saved)
        self.min_tags_input.valueChanged.connect(self.on_min_tags_changed)
        self.allow_multiple_toggle.stateChanged.connect(self.on_allow_multiple_changed)
        self.is_required_toggle.stateChanged.connect(self.on_is_required_changed)
        self.prevent_auto_scroll.stateChanged.connect(self.on_prevent_auto_scroll_changed)

    def set_tag_group(self, tag_group: TagGroup, is_scripted: bool = False):
        self.is_scripted = is_scripted

        self.active_group = tag_group
        self.group_label.setText(f"Editing: {tag_group.name}")
        self.name_edit.setText(tag_group.name)
        self.min_tags_input.setValue(tag_group.min_tags)
        self.allow_multiple_toggle.setChecked(tag_group.allow_multiple)
        self.is_required_toggle.setChecked(tag_group.is_required)
        self.prevent_auto_scroll.setChecked(tag_group.prevent_auto_scroll)

        self.is_scripted = False

        self._handle_button_states()

    def clear_tag_group(self):
        self.active_group = None
        self.group_label.setText("Editing:")
        self.name_edit.setText('')
        self._handle_button_states()

    def on_name_edit_changed(self):
        self._handle_button_states()

    def on_allow_multiple_changed(self,):
        self.min_tags_label.setEnabled(self.allow_multiple_toggle.isChecked())
        self.min_tags_input.setEnabled(self.allow_multiple_toggle.isChecked())
        self.active_group.allow_multiple = self.allow_multiple_toggle.isChecked()

        self._handle_button_states()
        self.group_updated.emit(self.active_group) if not self.is_scripted else None

    def on_is_required_changed(self):
        self.active_group.is_required = self.is_required_toggle.isChecked()

        self._handle_button_states()
        self.group_updated.emit(self.active_group) if not self.is_scripted else None

    def on_name_edit_saved(self):
        self.active_group.name = self.name_edit.text()
        self.group_label.setText(f"Editing: {self.active_group.name}")
        self.group_updated.emit(self.active_group) if not self.is_scripted else None

        self._handle_button_states()

    def on_min_tags_changed(self):
        if not self.allow_multiple_toggle.isChecked():
            self.min_tags_input.setValue(1)
            return
        
        self.active_group.min_tags = self.min_tags_input.value()
        self.group_updated.emit(self.active_group) if not self.is_scripted else None

        self._handle_button_states()

    def on_prevent_auto_scroll_changed(self):
        self.active_group.prevent_auto_scroll = self.prevent_auto_scroll.isChecked()
        self.group_updated.emit(self.active_group) if not self.is_scripted else None

        self._handle_button_states()

    def _handle_button_states(self):
        condition = self.active_group is not None
        
        self.name_edit.setEnabled(condition)
        self.is_required_toggle.setEnabled(condition)
        self.allow_multiple_toggle.setEnabled(condition)
        self.prevent_auto_scroll.setEnabled(condition)
        self.name_save_button.setEnabled(condition)
        self.min_tags_label.setEnabled(condition)
        self.min_tags_input.setEnabled(condition)
        
        if not condition:
            return
            
        self.name_save_button.setEnabled(self.name_edit.text() != '' and self.name_edit.text().strip() != self.active_group.name)

        self.min_tags_label.setEnabled(self.allow_multiple_toggle.isChecked())
        self.min_tags_input.setEnabled(self.allow_multiple_toggle.isChecked())

class TagGroupsSettings(SettingsWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.db: Database = parent.db
        self.active_project: Project = parent.project
        self.update_poller: UpdatePoller = parent.update_poller
        self.config_handler: ConfigHandler = parent.config_handler

        self.active_group = None
        self.selected_item = None  # Track the currently selected item
        self.setupUI()

    def navigate_path(self, path: str):
        # Find the TagGroup with the name of the path

        for i in range(self.tag_groups_list.count()):
            item = self.tag_groups_list.item(i)
            if item.tag_group.name.replace(' ', '_').replace('.', "_").lower() == path.strip():
                self.on_tag_group_clicked(item.tag_group)

    def setupUI(self):
        self.main_layout = QHBoxLayout(self)

        self._setup_left_column()
        self._setup_right_column()

    def _setup_left_column(self):
        column_layout = QVBoxLayout()

        tag_groups_label = QLabel("Tag Groups")
        tag_groups_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        column_layout.addWidget(tag_groups_label)

        add_layout = QHBoxLayout()
        add_button = QPushButton("Add Tag Group")

        self.add_group_name_input = QLineEdit()
        self.add_group_name_input.setPlaceholderText("Tag Group Name")

        add_button.clicked.connect(self.add_tag_group)
        self.add_group_name_input.returnPressed.connect(self.add_tag_group)

        add_layout.addWidget(add_button)
        add_layout.addWidget(self.add_group_name_input)

        self.tag_groups_list = QListWidget()
        # Enable drag and drop
        self.tag_groups_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.tag_groups_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        # Allow items to be dragged
        self.tag_groups_list.setDragEnabled(True)
        # Allow items to be dropped
        self.tag_groups_list.setAcceptDrops(True)
        # Make the list widget sort items according to drop position
        self.tag_groups_list.setMovement(QListWidget.Movement.Snap)

        for tag_group in self.db.tags.get_project_tags(self.active_project.id):
            tag_group_item = TagGroupListItem(tag_group=tag_group,
                                              database=self.db,
                                              update_poller=self.update_poller,
                                              delete_callback=self.remove_ui_component,
                                              list_widget=self.tag_groups_list,
                                              config_handler=self.config_handler,
                                              callback=self.on_tag_group_clicked
                                              )
            self.tag_groups_list.addItem(tag_group_item)

        # Connect the model's row moved signal to update the database
        self.tag_groups_list.model().rowsMoved.connect(self.update_tag_group_order)

        column_layout.addLayout(add_layout)
        column_layout.addWidget(self.tag_groups_list)

        self.main_layout.addLayout(column_layout)

    def _setup_right_column(self):
        column_layout = QVBoxLayout()

        self.edit_group_label = QLabel("Edit Group")
        self.edit_group_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        column_layout.addWidget(self.edit_group_label)

        add_layout = QHBoxLayout()
        self.add_tag_button = QPushButton("Add Tag")

        self.edit_tag_group_widget = TagGroupEditWidget(parent=self)
        self.edit_tag_group_widget.group_updated.connect(self.on_tag_group_updated)

        self.tags_label = QLabel("Tags")
        self.tags_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.add_tag_name_input = QLineEdit()
        self.add_tag_name_input.setPlaceholderText("Tag Name")

        self.add_tag_button.clicked.connect(self.add_tag)
        self.add_tag_button.setEnabled(False)

        self.add_tag_name_input.returnPressed.connect(self.add_tag)

        add_layout.addWidget(self.add_tag_button)
        add_layout.addWidget(self.add_tag_name_input)

        self.tags_list = QListWidget()
        # Enable drag and drop
        self.tags_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.tags_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        # Allow items to be dragged
        self.tags_list.setDragEnabled(True)
        # Allow items to be dropped
        self.tags_list.setAcceptDrops(True)
        # Make the list widget sort items according to drop position
        self.tags_list.setMovement(QListWidget.Movement.Snap)

        # Connect the model's row moved signal to update the database
        self.tags_list.model().rowsMoved.connect(self.update_tag_order)

        column_layout.addWidget(self.edit_tag_group_widget)
        column_layout.addWidget(self.tags_label)
        column_layout.addLayout(add_layout)
        column_layout.addWidget(self.tags_list)

        self.main_layout.addLayout(column_layout)

    def add_tag_group(self):
        name = self.add_group_name_input.text()

        if len(name) == 0:
            QMessageBox.warning(self, 'Invalid tag group', 'The name of a tag group cannot be empty')
            return
        
        if self.db.tags.tag_group_name_exists(name, self.active_project.id):
            QMessageBox.warning(self, 'Duplicate tag group', 'Tag group names must be unique within a project')
            return

        group_id = self.db.tags.add_tag_group(name, self.tag_groups_list.count(), self.active_project.id)
        group = TagGroup(group_id, self.active_project.id, name, self.tag_groups_list.count())
        self.tag_groups_list.addItem(TagGroupListItem(
            tag_group=group,
            database=self.db,
            update_poller=self.update_poller,
            delete_callback=self.remove_ui_component,
            list_widget=self.tag_groups_list,
            config_handler=self.config_handler,
            callback=self.on_tag_group_clicked))

        self.add_group_name_input.clear()
        self.on_tag_group_clicked(group)

        # Used to update the UI in the Tagging Page
        self.update_poller.poll_update('update_tag_groups')

    def add_tag(self):
        if self.active_group is None:
            return
        name = self.add_tag_name_input.text()

        if len(name) == 0:
            QMessageBox.warning(self, 'Invalid tag', 'The name of a tag cannot be empty')
            return
        
        if self.db.tags.tag_name_exists(name, self.active_group.id):
            QMessageBox.warning(self, 'Duplicate tag', 'Tag names must be unique within a tag group')
            return

        tag_id = self.db.tags.add_tag(name, self.active_group.id, self.tags_list.count())
        tag = Tag(tag_id, name, self.active_group.id)
        self.tags_list.addItem(TagListItem(tag=tag, database=self.db, update_poller=self.update_poller, delete_callback=self.remove_ui_component, list_widget = self.tags_list))

        self.add_tag_name_input.clear()

        # Used to update the UI in the Tagging Page
        self.update_poller.poll_update('update_tag_groups')

    def remove_ui_component(self, id: int, type: Literal['tag_group', 'tag']):
        if type == 'tag_group':
            for i in range(self.tag_groups_list.count()):
                item = self.tag_groups_list.item(i)
                if item.tag_group.id == id:
                    # Deselect the item before removal
                    if self.selected_item == item:
                        widget = self.tag_groups_list.itemWidget(item)
                        if widget:
                            widget.setSelected(False)
                        self.selected_item = None
                    
                    self.tag_groups_list.takeItem(i)
                    self.update_tag_group_order()
                    
                    if self.active_group is not None and id == self.active_group.id:
                        self.active_group = None
                        self.edit_tag_group_widget.clear_tag_group()
                        self.add_tag_button.setEnabled(False)
                        self.tags_list.clear()
                    break
        elif type == 'tag':
            for i in range(self.tags_list.count()):
                item = self.tags_list.item(i)
                if item.tag.id == id:
                    self.tags_list.takeItem(i)
                    self.update_tag_order()
                    break

    def update_tag_group_order(self):
        """Update the order of tag groups in the database after drag and drop"""
        items: list[TagGroupListItem] = []
        new_order: list[tuple[int, int]] = []
        
        # Collect all items
        for i in range(self.tag_groups_list.count()):
            items.append(self.tag_groups_list.item(i))
        
        # Reassign display orders sequentially starting from 0
        for i, item in enumerate(items):
            item.tag_group.display_order = i
            new_order.append((item.tag_group.id, i))
        
        self.db.tags.update_tag_group_order(new_order)
        self.update_poller.poll_update('update_tag_groups')

    def update_tag_order(self):
        """Update the order of tags in the database after drag and drop"""
        items: list[TagListItem] = []
        new_order: list[tuple[int, int]] = []
        
        # Collect all items
        for i in range(self.tags_list.count()):
            items.append(self.tags_list.item(i))
        
        # Reassign display orders sequentially starting from 0
        for i, item in enumerate(items):
            item.tag.display_order = i
            new_order.append((item.tag.id, i))
        
        self.db.tags.update_tag_order(new_order)
        self.update_poller.poll_update('update_tag_groups')

    def on_tag_group_clicked(self, group: TagGroup):
        if group.tags is None:
            group.tags = []
        
        # Find the clicked item
        clicked_item = None
        for i in range(self.tag_groups_list.count()):
            item = self.tag_groups_list.item(i)
            if item.tag_group.id == group.id:
                clicked_item = item
                break
        
        # Handle selection states
        if self.selected_item is not None:
            widget = self.tag_groups_list.itemWidget(self.selected_item)
            if widget:
                widget.setSelected(False)
        
        if clicked_item is not None:
            widget = self.tag_groups_list.itemWidget(clicked_item)
            if widget:
                widget.setSelected(True)
            self.selected_item = clicked_item
        
        # Update the rest of the UI
        self.tags_list.clear()
        self.active_group = group
        self.add_tag_button.setEnabled(True)
        self.edit_tag_group_widget.set_tag_group(group, True)
        
        for tag in group.tags:
            self.tags_list.addItem(TagListItem(
                tag=tag,
                database=self.db,
                update_poller=self.update_poller,
                delete_callback=self.remove_ui_component,
                list_widget=self.tags_list
            ))

    def on_tag_group_updated(self, group: TagGroup):
        self.db.tags.update_tag_group(group)
        # Used to update the UI in the Tagging Page
        self.update_poller.poll_update('update_tag_groups')