from PyQt6.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout, QLabel, QStackedWidget, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from src.tagging.tag_group import Tag
from src.styling.style_manager import StyleManager

class TagListItem(QWidget):
    deleteClicked = pyqtSignal(int)
    tagRenamed = pyqtSignal(int, str)
    focused = pyqtSignal(QWidget)

    def __init__(self, tag: Tag, style_manager: StyleManager, parent=None):
        self.tag = tag
        self.style_manager: StyleManager = style_manager

        super().__init__(parent)

        self.init_ui()

    def init_ui(self):
        container = QHBoxLayout()
        container.setContentsMargins(10, 10, 10, 10)

        self.indexLabel = QLabel(str(self.tag.display_order))
        self.indexLabel.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'panel_alt'))

        self.name_stack = QStackedWidget()

        self.nameLabel = QLabel(self.tag.name)
        self.nameLabel.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        self.nameLabel.setContentsMargins(10, 0, 0, 0)

        self.nameInput = QLineEdit(self.tag.name)
        self.nameInput.setStyleSheet(self.style_manager.get_stylesheet(QLineEdit))

        self.name_stack.addWidget(self.nameLabel)
        self.name_stack.addWidget(self.nameInput)

        self.button_stack = QStackedWidget()
        self.editButton = QPushButton("✏️")
        self.editButton.setFont(QFont("Arial", 12))
        self.confirmButton = QPushButton("✔")
        self.confirmButton.setFont(QFont("Arial", 12))

        self.editButton.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'panel'))
        self.editButton.setFixedHeight(32)
        self.editButton.setFixedWidth(40)
        self.confirmButton.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'accent'))
        self.confirmButton.setFixedHeight(32)
        self.confirmButton.setFixedWidth(40)

        self.button_stack.addWidget(self.editButton)
        self.button_stack.addWidget(self.confirmButton)

        self.deleteButton = QPushButton("🗑")
        self.deleteButton.setFont(QFont("Arial", 12))
        self.deleteButton.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'warning'))
        self.deleteButton.setFixedHeight(30)
        self.deleteButton.setFixedWidth(40)

        container.addWidget(self.indexLabel)
        container.addWidget(self.name_stack)
        container.addStretch(1)
        container.addWidget(self.button_stack)
        container.addWidget(self.deleteButton)

        self.setLayout(container)

        self.editButton.clicked.connect(self._edit_tag)
        self.confirmButton.clicked.connect(self._confirm_tag)
        self.deleteButton.clicked.connect(self._delete_tag)

    def rename_tag(self, new_name: str):
        name = self.old_name if new_name == '' else new_name
        self.nameLabel.setText(name)
        self.nameInput.setText(name)

        self.tagRenamed.emit(self.tag.id, name)

    def _edit_tag(self):
        self.focused.emit(self)

        self.name_stack.setCurrentIndex(1)
        self.button_stack.setCurrentIndex(1)

        self.old_name = self.nameInput.text()

        self.nameInput.setFocus()

    def _confirm_tag(self):
        self.focused.emit(self)

        self.name_stack.setCurrentIndex(0)
        self.button_stack.setCurrentIndex(0)
        self.rename_tag(self.nameInput.text())

    def _delete_tag(self):
        self.focused.emit(self)
        self.deleteClicked.emit(self.tag.id)

    def reset_state(self):
        self.name_stack.setCurrentIndex(0)
        self.button_stack.setCurrentIndex(0)
        self.nameInput.setText(self.nameLabel.text())

    def set_index_label(self, index: int):
        self.indexLabel.setText(str(index))