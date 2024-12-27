from typing import Callable, Literal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QLineEdit, QMessageBox
from PyQt6.QtCore import Qt

from src.project import Project
from src.database.database import Database
from src.tagging.tag_group import Tag, TagGroup
from src.update_poller import UpdatePoller

from PyQt6.QtCore import QTimer

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
        self.db.tags.delete_tag(self.tag.id)

        # Used to update the UI in the Tagging Page
        self.update_poller.poll_update('update_tag_groups')

        self.delete_callback(self.tag.id, 'tag')

class TagListItem(QListWidgetItem):
    def __init__(self, tag: Tag, database: Database, update_poller: UpdatePoller, delete_callback: Callable, list_widget: QListWidget):
        super().__init__(list_widget)
        self.tag = tag

        widget = TagWidget(tag=tag, database=database, update_poller=update_poller, delete_callback=delete_callback)

        list_widget.setItemWidget(self, widget)

        self.setSizeHint(widget.sizeHint())

class TagGroupWidget(QWidget):
    def __init__(self, tag_group: TagGroup, database: Database, update_poller: UpdatePoller, callback: Callable, delete_callback: Callable, parent=None):
        super().__init__(parent)
        self.tag_group = tag_group
        self.db: Database = database
        self.update_poller: UpdatePoller = update_poller
        self.callback = callback
        self.delete_callback = delete_callback
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout(self)
        
        button = QPushButton(self.tag_group.name)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.clicked.connect(self.on_button_clicked)

        required_button = QPushButton("R")
        required_button.setFixedWidth(30)
        required_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        min_tags_button = QPushButton(str(self.tag_group.min_tags))
        min_tags_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        min_tags_button.setFixedWidth(40)
        min_tags_button.setDisabled(True)

        delete_button = QPushButton("-")
        delete_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        delete_button.setFixedWidth(30)
        delete_button.clicked.connect(self.delete_tag_group)

        self.main_layout.addWidget(button)
        self.main_layout.addWidget(required_button)
        self.main_layout.addWidget(min_tags_button)
        self.main_layout.addWidget(delete_button)

    def on_button_clicked(self):
        # Make sure the tag group is updated
        self.tag_group = self.db.tags.get_tag_group(self.tag_group.id)
        self.callback(self.tag_group)

    def delete_tag_group(self):
        # Display a dialog to confirm deletion
        result = QMessageBox.question(self, "Delete Tag Group", "Are you sure you want to delete this tag group?\nThis action cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Yes:
            self.db.tags.delete_tag_group(self.tag_group.id)

            # Used to update the UI in the Tagging Page
            self.update_poller.poll_update('update_tag_groups')

            self.delete_callback(self.tag_group.id, 'tag_group')

class TagGroupListItem(QListWidgetItem):
    def __init__(self, tag_group: TagGroup, database: Database, update_poller: Callable, delete_callback: Callable, list_widget: QListWidget, callback: Callable):
        super().__init__(list_widget)
        self.tag_group = tag_group
        
        # Create the widget that will be displayed in the list item
        widget = TagGroupWidget(tag_group=tag_group, database=database, delete_callback=delete_callback, update_poller=update_poller, callback=callback)
        
        # Set the widget for this list item
        list_widget.setItemWidget(self, widget)
        
        # Set an appropriate size for the item
        self.setSizeHint(widget.sizeHint())


class TagGroupsSettings(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.db: Database = parent.db
        self.active_project: Project = parent.project
        self.update_poller: UpdatePoller = parent.update_poller

        self.active_group = None
        self.setupUI()

    def setupUI(self):
        self.main_layout = QHBoxLayout(self)

        self._setup_left_column()
        self._setup_right_column()

    def _setup_left_column(self):
        column_layout = QVBoxLayout()

        tag_groups_label = QLabel("Tag Groups")
        column_layout.addWidget(tag_groups_label)

        add_layout = QHBoxLayout()
        add_button = QPushButton("Add Tag Group")

        self.add_group_name_input = QLineEdit()
        self.add_group_name_input.setPlaceholderText("Tag Group Name")

        add_button.clicked.connect(self.add_tag_group)

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
            tag_group_item = TagGroupListItem(tag_group=tag_group, database=self.db, update_poller=self.update_poller, delete_callback=self.remove_ui_component, list_widget=self.tag_groups_list, callback=self.on_tag_group_clicked)
            self.tag_groups_list.addItem(tag_group_item)

        # Connect the model's row moved signal to update the database
        self.tag_groups_list.model().rowsMoved.connect(self.update_tag_group_order)

        column_layout.addLayout(add_layout)
        column_layout.addWidget(self.tag_groups_list)

        self.main_layout.addLayout(column_layout)

    def _setup_right_column(self):
        column_layout = QVBoxLayout()

        self.tags_label = QLabel("Tags")
        column_layout.addWidget(self.tags_label)

        add_layout = QHBoxLayout()
        self.add_tag_button = QPushButton("Add Tag")

        self.add_tag_name_input = QLineEdit()
        self.add_tag_name_input.setPlaceholderText("Tag Name")

        self.add_tag_button.clicked.connect(self.add_tag)
        self.add_tag_button.setEnabled(False)

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
        self.tag_groups_list.addItem(TagGroupListItem(tag_group=group, database=self.db, update_poller=self.update_poller, delete_callback=self.remove_ui_component, list_widget=self.tag_groups_list, callback=self.on_tag_group_clicked))

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

        # Used to update the UI in the Tagging Page
        self.update_poller.poll_update('update_tag_groups')

    def remove_ui_component(self, id: int, type: Literal['tag_group', 'tag']):
        if type == 'tag_group':
            for i in range(self.tag_groups_list.count()):
                item = self.tag_groups_list.item(i)
                if item.tag_group.id == id:
                    self.tag_groups_list.takeItem(i)
                    if self.active_group is not None and id == self.active_group.id:
                        self.active_group = None
                        self.add_tag_button.setEnabled(False)
                        self.tags_list.clear()
                        self.tags_label.setText("Tags")
                    break
        elif type == 'tag':
            for i in range(self.tags_list.count()):
                item = self.tags_list.item(i)
                if item.tag.id == id:
                    self.tags_list.takeItem(i)
                    break

    def update_tag_group_order(self):
        """Update the order of tag groups in the database after drag and drop"""
        items: list[TagGroupListItem] = []
        new_order: list[tuple[int, int]] = []
        for i in range(self.tag_groups_list.count()):
            item = self.tag_groups_list.item(i)
            items.append(item)

        for i in range(len(items)):
            item = items[i]
            item.tag_group.display_order = i
            new_order.append((item.tag_group.id, i))

        self.db.tags.update_tag_group_order(new_order)

        # Used to update the UI in the Tagging Page
        self.update_poller.poll_update('update_tag_groups')

    def update_tag_order(self):
        """Update the order of tags in the database after drag and drop"""
        items: list[TagListItem] = []
        new_order: list[tuple[int, int]] = []
        for i in range(self.tags_list.count()):
            item = self.tags_list.item(i)
            items.append(item)

        for i in range(len(items)):
            item = items[i]
            item.tag.display_order = i
            new_order.append((item.tag.id, i))

        self.db.tags.update_tag_order(new_order)

        # Used to update the UI in the Tagging Page
        self.update_poller.poll_update('update_tag_groups')

    def on_tag_group_clicked(self, group: TagGroup):
        if group.tags is None: 
            group.tags = []

        self.tags_list.clear()
        self.active_group = group
        self.add_tag_button.setEnabled(True)

        for tag in group.tags:
            self.tags_list.addItem(TagListItem(tag=tag, database=self.db, update_poller=self.update_poller, delete_callback=self.remove_ui_component, list_widget=self.tags_list))

        self.tags_label.setText(f"Tags for \"{group.name}\"")