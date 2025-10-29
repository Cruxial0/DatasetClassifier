from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QRect, QPoint
from PyQt6.QtGui import QColor, QPalette
from typing import List, Union
from PyQt6.QtWidgets import QApplication
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
        
        if isinstance(self.item, Tag):
            self.setup_tag_ui()
        elif isinstance(self.item, TagGroup):
            self.setup_taggroup_ui()
        else:
            print(f"Unknown item type: {type(self.item)}")
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
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

class TagCompleterPopup(QWidget):
    item_selected = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(0)
        
        self.container = QFrame()
        self.container.setObjectName("completerContainer")
        self.container.setStyleSheet("""
            QFrame#completerContainer {
                background-color: white;
                border: 1px solid #aaaaaa;
                border-radius: 4px;
            }
        """)
        self.container.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(4, 4, 4, 4)
        self.container_layout.setSpacing(2)
        self.main_layout.addWidget(self.container)

    def update_items(self, items: List[Union[Tag, TagGroup]]):
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for item in items:
            widget = TagItemWidget(item)
            widget.clicked.connect(self.on_item_clicked)
            self.container_layout.addWidget(widget)

        self.adjustSize()
        max_height = min(300, self.sizeHint().height())
        self.setFixedHeight(max_height)

    def on_item_clicked(self, item):
        self.item_selected.emit(item)
        self.hide()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.hide()

from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QRect, QPoint
from PyQt6.QtGui import QColor, QPalette
from typing import List, Union
from PyQt6.QtWidgets import QApplication
from src.tagging.tag_group import Tag, TagGroup

class TagSearchWidget(QWidget):
    item_selected = pyqtSignal(object)

    def __init__(self, db_query_func):
        super().__init__()
        self.db_query_func = db_query_func
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.search_input = QLineEdit()
        self.search_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.search_input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.search_input)

        self.popup = TagCompleterPopup(self)
        self.popup.item_selected.connect(self.on_item_selected)

    def on_text_changed(self, text: str):
        if not text:
            self.popup.hide()
            return

        items = self.db_query_func(text)
        
        if items:
            self.popup.update_items(items)
            pos = self.search_input.mapToGlobal(self.search_input.rect().bottomLeft())
            self.popup.setFixedWidth(self.search_input.width())
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

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            popup_geo = self.popup.geometry()
            input_pos = self.search_input.mapToGlobal(QPoint(0, 0))
            input_geo = QRect(input_pos, self.search_input.size())
            global_pos = event.globalPosition().toPoint()  # Updated to globalPosition()
            if not (popup_geo.contains(global_pos) or input_geo.contains(global_pos)):
                self.popup.hide()
                return True
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        app = QApplication.instance()
        if app and not hasattr(self, '_event_filter_installed'):
            app.installEventFilter(self)
            self._event_filter_installed = True

    def hideEvent(self, event):
        super().hideEvent(event)
        self.popup.hide()