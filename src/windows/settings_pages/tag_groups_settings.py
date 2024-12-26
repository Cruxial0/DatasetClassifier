from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QSizePolicy, QLineEdit
from PyQt6.QtCore import Qt

from src.database.database import Database

class TagWidget(QWidget):
    def __init__(self, tag, parent=None):
        super().__init__(parent)
        self.tag = tag
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout(self)

        self.line_edit = QLineEdit(self.tag.name)
        self.line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.main_layout.addWidget(self.line_edit)

class TagListItem(QListWidgetItem):
    def __init__(self, tag, list_widget):
        super().__init__(list_widget)

class TagGroupWidget(QWidget):
    def __init__(self, tag_group, parent=None):
        super().__init__(parent)
        self.tag_group = tag_group
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout(self)
        
        button = QPushButton(self.tag_group.name)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        required_button = QPushButton("R")
        required_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        min_tags_button = QPushButton(str(self.tag_group.min_tags))
        min_tags_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        min_tags_button.setDisabled(True)

        self.main_layout.addWidget(button)
        self.main_layout.addWidget(required_button)
        self.main_layout.addWidget(min_tags_button)

class TagGroupListItem(QListWidgetItem):
    def __init__(self, tag_group, list_widget):
        super().__init__(list_widget)
        self.tag_group = tag_group
        
        # Create the widget that will be displayed in the list item
        widget = TagGroupWidget(tag_group)
        
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

        add_name_input = QLineEdit()
        add_name_input.setPlaceholderText("Tag Group Name")

        add_layout.addWidget(add_button)
        add_layout.addWidget(add_name_input)

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
            tag_group_item = TagGroupListItem(tag_group, self.tag_groups_list)
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

        add_name_input = QLineEdit()
        add_name_input.setPlaceholderText("Tag Name")

        add_layout.addWidget(add_button)
        add_layout.addWidget(add_name_input)

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
        self.tags_list.model().rowsMoved.connect(self.update_tag_group_order)

        column_layout.addLayout(add_layout)
        column_layout.addWidget(self.tags_list)

        self.main_layout.addLayout(column_layout)

    def update_tag_group_order(self):
        """Update the order of tag groups in the database after drag and drop"""
        new_order = []
        for i in range(self.tag_groups_list.count()):
            item = self.tag_groups_list.item(i)
            new_order.append(item.tag_group.id)
        
        # Assuming your database has a method to update the order
        # You'll need to implement this method in your Database class
        self.db.tags.update_tag_group_order(self.active_project.id, new_order)