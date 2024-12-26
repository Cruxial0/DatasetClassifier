from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QLineEdit
from PyQt6.QtCore import Qt

from src.database.database import Database
from src.tagging.tag_group import Tag, TagGroup

from PyQt6.QtCore import QTimer

class TagWidget(QWidget):
    def __init__(self, tag, database, parent=None):
        super().__init__(parent)
        self.tag: Tag = tag
        self.db: Database = database
        
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

        self.main_layout.addWidget(self.line_edit)

    def write_tag(self):
        # Reset and start timer
        self.write_timer.stop()  # Stop any existing timer
        self.write_timer.start()  # Start the timer again
        
    def _write_tag_to_db(self):
        # This is called after the timer expires
        self.tag.name = self.line_edit.text()
        self.db.tags.update_tag(self.tag)

class TagListItem(QListWidgetItem):
    def __init__(self, tag, database, list_widget):
        super().__init__(list_widget)
        self.tag = tag

        widget = TagWidget(tag, database)

        list_widget.setItemWidget(self, widget)

        self.setSizeHint(widget.sizeHint())

class TagGroupWidget(QWidget):
    def __init__(self, tag_group, callback, parent=None):
        super().__init__(parent)
        self.tag_group = tag_group
        self.callback = callback
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout(self)
        
        button = QPushButton(self.tag_group.name)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.clicked.connect(self.on_button_clicked)

        required_button = QPushButton("R")
        required_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        min_tags_button = QPushButton(str(self.tag_group.min_tags))
        min_tags_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        min_tags_button.setDisabled(True)

        self.main_layout.addWidget(button)
        self.main_layout.addWidget(required_button)
        self.main_layout.addWidget(min_tags_button)

    def on_button_clicked(self):
        self.callback(self.tag_group)

class TagGroupListItem(QListWidgetItem):
    def __init__(self, tag_group, list_widget, callback):
        super().__init__(list_widget)
        self.tag_group = tag_group
        
        # Create the widget that will be displayed in the list item
        widget = TagGroupWidget(tag_group, callback)
        
        # Set the widget for this list item
        list_widget.setItemWidget(self, widget)
        
        # Set an appropriate size for the item
        self.setSizeHint(widget.sizeHint())


class TagGroupsSettings(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.db: Database = parent.db
        self.active_project = parent.project
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
            tag_group_item = TagGroupListItem(tag_group, self.tag_groups_list, self.on_tag_group_clicked)
            self.tag_groups_list.addItem(tag_group_item)

        # Connect the model's row moved signal to update the database
        self.tag_groups_list.model().rowsMoved.connect(self.update_tag_group_order)

        column_layout.addLayout(add_layout)
        column_layout.addWidget(self.tag_groups_list)

        self.main_layout.addLayout(column_layout)

    def _setup_right_column(self):
        column_layout = QVBoxLayout()

        tags_label = QLabel("Tags")
        column_layout.addWidget(tags_label)

        add_layout = QHBoxLayout()
        add_button = QPushButton("Add Tag")

        self.add_tag_name_input = QLineEdit()
        self.add_tag_name_input.setPlaceholderText("Tag Name")

        add_button.clicked.connect(self.add_tag)

        add_layout.addWidget(add_button)
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
        group_id = self.db.tags.add_tag_group(name, self.tag_groups_list.count(), self.active_project.id)
        group = TagGroup(group_id, self.active_project.id, name, self.tag_groups_list.count())
        self.tag_groups_list.addItem(TagGroupListItem(group, self.tag_groups_list, self.on_tag_group_clicked))

    def add_tag(self):
        if self.active_group is None:
            return
        name = self.add_tag_name_input.text()
        tag_id = self.db.tags.add_tag(name, self.active_group.id, self.tags_list.count())
        tag = Tag(tag_id, name, self.active_group.id)
        self.tags_list.addItem(TagListItem(tag, self.db, self.tags_list))

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

    def on_tag_group_clicked(self, group: TagGroup):
        if group.tags is None: 
            group.tags = []
            
        self.tags_list.clear()
        self.active_group = group

        for tag in group.tags:
            self.tags_list.addItem(TagListItem(tag, self.db, self.tags_list))