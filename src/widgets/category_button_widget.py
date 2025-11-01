"""
Custom widget for category buttons in the scoring page.
Combines the category button, remove button, and keybind label into one cohesive component.

Usage:
    Place this file in your src/widgets/ directory.
    Import in scoring_page.py: from src.widgets.category_button_widget import CategoryButtonWidget
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from src.styling.style_manager import StyleManager


class CategoryButtonWidget(QWidget):
    """
    A custom widget that encapsulates a category button with its keybind label and remove button.
    
    Signals:
        clicked: Emitted when the category button is clicked, passes the category name
        removeRequested: Emitted when the remove button is clicked, passes self
    """
    
    clicked = pyqtSignal(str)  # category name
    removeRequested = pyqtSignal(object)  # self
    
    def __init__(self, category_name: str, index: int, style_manager: StyleManager, parent=None):
        """
        Initialize the category button widget.
        
        Args:
            category_name: The name of the category
            index: The index of this category (0-9)
            style_manager: The style manager for applying styles
            parent: The parent widget
        """
        super().__init__(parent)
        self.category_name = category_name
        self.index = index
        self.style_manager = style_manager
        self.is_active = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        
        # Keybind label (left side)
        self.keybind_label = QLabel()
        self.keybind_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel, 'keybind'))
        self.keybind_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.keybind_label.setFixedWidth(60)
        self.keybind_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        
        # Category button (center, expanding)
        self.category_button = QPushButton(self.category_name)
        self.category_button.setStyleSheet(self.style_manager.get_stylesheet(QPushButton))
        self.category_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.category_button.setMinimumHeight(30)
        self.category_button.clicked.connect(self._on_button_clicked)
        
        # Remove button (right side)
        self.remove_button = QPushButton("×")
        self.remove_button.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'warning'))
        self.remove_button.setFixedSize(30, 30)
        self.remove_button.setToolTip("Remove this category")
        
        # Make the × larger and centered
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.remove_button.setFont(font)
        
        self.remove_button.clicked.connect(self._on_remove_clicked)
        
        # Add widgets to layout
        layout.addWidget(self.keybind_label)
        layout.addWidget(self.category_button)
        layout.addWidget(self.remove_button)
        
        self.setLayout(layout)
    
    def _on_button_clicked(self):
        """Handle button click"""
        self.clicked.emit(self.category_name)
    
    def _on_remove_clicked(self):
        """Handle remove button click"""
        self.removeRequested.emit(self)
    
    def set_keybind_text(self, text: str):
        """Update the keybind label text"""
        self.keybind_label.setText(text)
    
    def set_active(self, active: bool):
        """Set the active state of the category button"""
        self.is_active = active
        if active:
            self.category_button.setStyleSheet(
                self.style_manager.get_stylesheet(QPushButton, 'accent')
            )
            self.keybind_label.setStyleSheet(
                self.style_manager.get_stylesheet(QLabel, 'keybind_accent')
            )
        else:
            self.category_button.setStyleSheet(
                self.style_manager.get_stylesheet(QPushButton)
            )
            self.keybind_label.setStyleSheet(
                self.style_manager.get_stylesheet(QLabel, 'keybind')
            )
    
    def get_category_name(self) -> str:
        """Return the category name"""
        return self.category_name
    
    def get_button(self) -> QPushButton:
        """Return the internal category button (for keybind registration)"""
        return self.category_button
    
    def click(self):
        """Programmatically click the button"""
        self.category_button.click()