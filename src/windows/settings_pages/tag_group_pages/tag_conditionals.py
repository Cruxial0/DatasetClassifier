from typing import List, Union
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QComboBox
from PyQt6.QtGui import QFont

from src.windows.settings_pages.settings_widget import SettingsWidget
from src.styling.style_manager import StyleManager
from src.tagging.tag_group import Tag, TagGroup
from src.widgets.tag_search_widget import TagSearchWidget

class ConditionalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.style_manager: StyleManager = parent.style_manager
        self.options = ["IF", "NOT", "AND", "OR"]
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        self.conditions = QComboBox(self)
        self.conditions.setStyleSheet(self.style_manager.get_stylesheet(QComboBox))
        self.conditions.addItems(self.options)
        self.conditions.setFixedWidth(70)

        layout.addWidget(self.conditions)

        def query_database(search_term: str) -> List[Union[Tag, TagGroup]]:
            tag = Tag(1, "example_tag", 100)
            group = TagGroup(id=1, project_id=0, name="example group", order=0)
            group.verify_self()
            return [tag, group]
        
        search_box = TagSearchWidget(query_database)
        search_box.setStyleSheet(self.style_manager.get_stylesheet(TagSearchWidget))
        layout.addWidget(search_box)

        self.setLayout(layout)

class TagConditionalsPage(SettingsWidget):
    def __init__(self, parent=None, **kwargs):
        self.tag_group = kwargs.get('tag_group', None)
        super().__init__(parent)
    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Tag Conditionals")
        title.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        conditionals = ConditionalWidget(self)
        layout.addWidget(conditionals)

        self.setLayout(layout)