from typing import Callable, Literal
from PyQt6.QtWidgets import (QListWidgetItem, QWidget, QHBoxLayout, 
                            QVBoxLayout, QLabel, QPushButton, 
                            QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from src.tagging.tag_group import TagGroup
from src.styling.style_manager import StyleManager

class TagGroupListWidget(QListWidgetItem):
    def __init__(self, tag_group: TagGroup, style_manager: StyleManager, callback: Callable[[Literal['edit', 'tags', 'activation'], TagGroup], None], parent=None):
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
        
        # Left side with title and details
        left_side = QVBoxLayout()
        
        # Title
        title = QLabel(self.tag_group.name)
        title.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        title_font = QFont("Arial", 12, QFont.Weight.Bold)
        title.setFont(title_font)
        
        # Details
        details = QLabel(f"{len(self.tag_group.tags)} tags · {'Required' if self.tag_group.is_required else 'Optional'}")
        details.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'subtext'))
        
        left_side.addWidget(title)
        left_side.addWidget(details)
        
        # Right side with buttons
        right_side = QHBoxLayout()
        right_side.setSpacing(8)
        
        # Create buttons
        settings_btn = self.create_button("⚙️", "General Settings")
        settings_btn.clicked.connect(lambda: self.callback('edit', self.tag_group))
        tags_btn = self.create_button("🏷️", "Tags")
        next_btn = self.create_button("▶️", "Conditional Activation")
        
        right_side.addWidget(settings_btn)
        right_side.addWidget(tags_btn)
        right_side.addWidget(next_btn)        
            
        container.addLayout(left_side)
        container.addStretch()
        container.addLayout(right_side)
        
        self.widget.setLayout(container)
        self.setSizeHint(self.widget.sizeHint())
        
    def create_button(self, text, tooltip):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(28, 28)
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
