from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout, QFrame, 
    QLabel, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from typing import List, Union

from src.tagging.tag_group import Tag, TagGroup

class TagItemWidget(QFrame):
    clicked = pyqtSignal(object)

    def __init__(self, item: Union[Tag, TagGroup]):
        super().__init__()
        self.item = item
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Different styling based on item type
        if isinstance(self.item, Tag):
            self.setup_tag_ui()
        elif isinstance(self.item, TagGroup):
            self.setup_taggroup_ui()
        else:
            print(f"Unknown item type: {type(self.item)}")  # Debug print
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setAutoFillBackground(True)
        
    def setup_tag_ui(self):
        layout = self.layout()
        name_label = QLabel(f"<b>{self.item.name}</b>")
        order_label = QLabel(f"Order: {self.item.display_order}")
        layout.addWidget(name_label)
        layout.addWidget(order_label)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0ff"))
        self.setPalette(palette)

    def setup_taggroup_ui(self):
        layout = self.layout()
        name_label = QLabel(f"<b>{self.item.name}</b> (Group)")
        tags_label = QLabel(f"Tags: {len(self.item.tags) if self.item.tags else 0}")
        info_label = QLabel(
            f"Required: {'Yes' if self.item.is_required else 'No'}, "
            f"Multiple: {'Yes' if self.item.allow_multiple else 'No'}, "
            f"Min Tags: {self.item.min_tags}"
        )
        
        layout.addWidget(name_label)
        layout.addWidget(tags_label)
        layout.addWidget(info_label)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#fff0f0"))
        self.setPalette(palette)

    def mousePressEvent(self, event):
        self.clicked.emit(self.item)

class TagCompleterPopup(QScrollArea):
    item_selected = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)
        self.setWidget(self.container)

    def update_items(self, items: List[Union[Tag, TagGroup]]):       
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for item in items:
            widget = TagItemWidget(item)
            widget.clicked.connect(lambda x=item: self.on_item_clicked(x))
            self.container_layout.addWidget(widget)

        self.adjustSize()
    
    def on_item_clicked(self, item):
        self.item_selected.emit(item)

class TagSearchWidget(QWidget):
    item_selected = pyqtSignal(object)

    def __init__(self, db_query_func):
        super().__init__()
        self.db_query_func = db_query_func
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.search_input)

        self.popup = TagCompleterPopup()
        self.popup.item_selected.connect(self.on_item_selected)

    def on_text_changed(self, text: str):
        if not text:
            self.popup.hide()
            return

        items = self.db_query_func(text)
        
        if items:
            self.popup.update_items(items)
            pos = self.search_input.mapToGlobal(self.search_input.rect().bottomLeft())
            self.popup.move(pos)
            self.popup.show()
        else:
            self.popup.hide()

    def on_item_selected(self, item):
        if item is None:
            return
            
        self.search_input.setText(item.name)
        self.popup.hide()
        self.item_selected.emit(item)