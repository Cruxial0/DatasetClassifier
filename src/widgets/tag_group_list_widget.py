from typing import Callable, Literal
from PyQt6.QtWidgets import (QListWidgetItem, QWidget, QHBoxLayout, 
                            QVBoxLayout, QLabel, QPushButton, 
                            QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from src.tagging.tag_group import TagGroup
from src.styling.style_manager import StyleManager

class TagGroupListWidget(QListWidgetItem):
    def __init__(self, tag_group: TagGroup, style_manager: StyleManager, callback: Callable[[Literal['edit', 'tags', 'activation', 'delete'], TagGroup], None], parent=None):
        super().__init__(parent)
        self.tag_group = tag_group
        self.style_manager = style_manager
        self.callback = callback

        self.widget = QWidget()
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        container = QHBoxLayout()
        container.setContentsMargins(16, 12, 16, 12)
        
        # Text section
        text_section = QVBoxLayout()
        
        # Title
        self.title = QLabel(self.tag_group.name)
        self.title.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        title_font = QFont("Arial", 12, QFont.Weight.Bold)
        self.title.setFont(title_font)
        
        # Details
        self.details = QLabel(f"{len(self.tag_group.tags)} tags · {'Required' if self.tag_group.is_required else 'Optional'}")
        self.details.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'subtext'))
        
        text_section.addWidget(self.title)
        text_section.addWidget(self.details)
        
        # Right side with action buttons
        right_side = QHBoxLayout()
        right_side.setSpacing(8)
        
        # Create buttons
        settings_btn = self.create_button("⚙️", "General Settings")
        settings_btn.clicked.connect(lambda: self.callback('edit', self.tag_group))
        tags_btn = self.create_button("🏷️", "Tags")
        tags_btn.clicked.connect(lambda: self.callback('tags', self.tag_group))
        next_btn = self.create_button("▶️", "Conditional Activation")
        next_btn.clicked.connect(lambda: self.callback('activation', self.tag_group))
        delete_btn = self.create_button("🗑️", "Delete Group", is_delete=True)
        delete_btn.clicked.connect(lambda: self.callback('delete', self.tag_group))
        
        right_side.addWidget(settings_btn)
        right_side.addWidget(tags_btn)
        right_side.addWidget(next_btn)
        right_side.addWidget(delete_btn)
            
        container.addLayout(text_section)
        container.addStretch()
        container.addLayout(right_side)
        
        self.widget.setLayout(container)
        self.setSizeHint(self.widget.sizeHint())
        
    def create_button(self, text, tooltip, is_delete=False):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(28, 28)
        
        if is_delete:
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #963535;
                    border-radius: 4px;
                    padding: 5px;
                    color: #963535;
                }
                QPushButton:hover {
                    background-color: #963535;
                    color: white;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #767676;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
        return btn
    
    def update_group(self, tag_group: TagGroup):
        self.tag_group = tag_group
        self.title.setText(self.tag_group.name)
        self.details.setText(f"{len(self.tag_group.tags)} tags · {'Required' if self.tag_group.is_required else 'Optional'}")