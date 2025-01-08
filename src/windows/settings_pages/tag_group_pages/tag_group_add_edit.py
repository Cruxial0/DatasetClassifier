from typing import Literal
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QSpinBox, QCheckBox, QPushButton, QSpacerItem)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from src.windows.settings_pages.settings_widget import SettingsWidget
from src.tagging.tag_group import TagGroup

class TagGroupAddOrEditPage(SettingsWidget):
    cancelled: pyqtSignal = pyqtSignal()
    onSave: pyqtSignal = pyqtSignal(TagGroup)
    onCreate: pyqtSignal = pyqtSignal(TagGroup)
    def __init__(self, parent=None, **kwargs):
        self.selected_group: TagGroup = None
        self.mode: Literal['add', 'edit'] = 'add'
        self.is_initialized = False

        super().__init__(parent)
        self.blockSignals(True)

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        self.title = QLabel(
            "Edit Tag Group" if self.mode == 'edit' else "New Tag Group"
        )
        self.title.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        self.title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.title)
        
        # Name input
        name_label = QLabel("Name")
        name_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(self.style_manager.get_stylesheet(QLineEdit))
        self.name_input.setPlaceholderText("Enter group name")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        
        layout.addSpacerItem(QSpacerItem(0, 10))
        
        # Required checkbox
        required_layout = QHBoxLayout()
        required_label_layout = QVBoxLayout()
        required_label = QLabel("Required")
        required_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        required_desc = QLabel("Make this group mandatory")
        required_desc.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'subtext'))
        required_label_layout.addWidget(required_label)
        required_label_layout.addWidget(required_desc)
        self.required_checkbox = QCheckBox()
        required_layout.addLayout(required_label_layout)
        required_layout.addWidget(self.required_checkbox, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(required_layout)
        
        # Allow multiple checkbox
        multiple_layout = QHBoxLayout()
        multiple_label_layout = QVBoxLayout()
        multiple_label = QLabel("Allow Multiple")
        multiple_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        multiple_desc = QLabel("Allow multiple tags selection")
        multiple_desc.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'subtext'))
        multiple_label_layout.addWidget(multiple_label)
        multiple_label_layout.addWidget(multiple_desc)
        self.multiple_checkbox = QCheckBox()
        # self.multiple_checkbox.setStyleSheet(self.style_manager.get_stylesheet(QCheckBox))
        multiple_layout.addLayout(multiple_label_layout)
        multiple_layout.addWidget(self.multiple_checkbox, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(multiple_layout)
        layout.addSpacerItem(QSpacerItem(0, 10))
        
        # Minimum tags spinbox
        min_tags_label = QLabel("Minimum Tags")
        min_tags_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        self.min_tags_spin = QSpinBox()
        self.min_tags_spin.setStyleSheet(self.style_manager.get_stylesheet(QSpinBox))
        self.min_tags_spin.setMinimum(0)
        layout.addWidget(min_tags_label)
        layout.addWidget(self.min_tags_spin)
        layout.addStretch(1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(self.style_manager.get_stylesheet(QPushButton))
        self.save_button = QPushButton("Save Changes")
        self.save_button.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'accept'))
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.name_input.textChanged.connect(self._edit_group)
        self.min_tags_spin.valueChanged.connect(self._edit_group)
        self.required_checkbox.stateChanged.connect(self._edit_group)
        self.multiple_checkbox.stateChanged.connect(self._edit_group)

        # Connect signals
        self.cancel_button.clicked.connect(self.cancelled)
        self.save_button.clicked.connect(self._on_save_clicked)

    def set_group(self, group: TagGroup):
        if self.mode == 'edit':
            self.selected_group = group
            self._update_button_states()

    def set_mode(self, mode: Literal['add', 'edit']):
        """
        Sets the mode of the page to either 'add' or 'edit'. Resets the selected group.

        Args:
            mode (Literal['add', 'edit']): The mode to set for the page.
        """

        self.selected_group = None
        self.mode = mode
        self._update_button_states()

    def _edit_group(self):
        """Sets values of selected group to those indicated by buttons."""
        
        if self.mode == 'add' and self.selected_group is None:
            self.selected_group = TagGroup(
                id=-1, # Will be corrected
                project_id=-1, # Will be corrected
                order=-1, # Will be corrected
                name=self.name_input.text(), 
                is_required=self.required_checkbox.isChecked(), 
                allow_multiple=self.multiple_checkbox.isChecked(), 
                min_tags=self.min_tags_spin.value())
        elif self.selected_group is not None:
            self.selected_group.name = self.name_input.text()
            self.selected_group.is_required = self.required_checkbox.isChecked()
            self.selected_group.allow_multiple = self.multiple_checkbox.isChecked()
            self.selected_group.min_tags = self.min_tags_spin.value()
        
        self._update_button_states()

    def _on_save_clicked(self):
        if self.mode == 'add':
            self.onCreate.emit(TagGroup(
                name=self.name_input.text(), 
                is_required=self.required_checkbox.isChecked(), 
                allow_multiple=self.multiple_checkbox.isChecked(), 
                min_tags=self.min_tags_spin.value()))
        else:
            self.onSave.emit(self.selected_group)

    def _update_button_states(self):
        self._block_signals(True)
        
        # Update button values
        if self.selected_group is not None:
            self.name_input.setText(self.selected_group.name)
            self.required_checkbox.setChecked(self.selected_group.is_required)
            self.multiple_checkbox.setChecked(self.selected_group.allow_multiple)
            self.min_tags_spin.setValue(self.selected_group.min_tags)
        else:
            self.name_input.setText('')
            self.required_checkbox.setChecked(True)
            self.multiple_checkbox.setChecked(False)
            self.min_tags_spin.setValue(1)

        self._block_signals(False)

        if self.mode == 'edit':
            self.title = "Edit Tag Group"
            self.save_button.setText("Save Changes")
        else:
            self.title = "New Tag Group"
            self.save_button.setText("Create Tag Group")

        # Update enabled states
        self.save_button.setEnabled(self.name_input.text() != '')
        self.min_tags_spin.setEnabled(self.multiple_checkbox.isChecked())

    def _block_signals(self, block: bool):
        self.name_input.blockSignals(block)
        self.required_checkbox.blockSignals(block)
        self.multiple_checkbox.blockSignals(block)
        self.min_tags_spin.blockSignals(block)