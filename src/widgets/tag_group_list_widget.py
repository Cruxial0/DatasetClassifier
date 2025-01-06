from PyQt6.QtWidgets import (QListWidgetItem, QWidget, QHBoxLayout, 
                            QVBoxLayout, QLabel, QPushButton, 
                            QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from src.tagging.tag_group import TagGroup

class TagGroupListWidget(QListWidgetItem):
    def __init__(self, tag_group: TagGroup, indent=0, parent=None):
        super().__init__(parent)
        self.tag_group = tag_group

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
        title_font = QFont("Arial", 12, QFont.Weight.Bold)
        title.setFont(title_font)
        
        # Details
        details = QLabel(f"{len(self.tag_group.tags)} tags · {'Required' if self.tag_group.is_required else 'Optional'}")
        details.setStyleSheet("color: gray; font-size: 12px;")
        
        left_side.addWidget(title)
        left_side.addWidget(details)
        
        # Right side with buttons
        right_side = QHBoxLayout()
        right_side.setSpacing(8)
        
        # Create buttons
        settings_btn = self.create_button("⚙️", "General Settings")
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
