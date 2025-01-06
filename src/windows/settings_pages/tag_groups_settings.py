import random
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget, QListWidget, QSizePolicy
from src.windows.settings_pages.settings_widget import SettingsWidget
from src.widgets.tag_group_list_widget import TagGroupListWidget

class TagGroupSettings(SettingsWidget):
    def __init__(self, parent=None):
        self._pages = {}
        self._page_creators = {
            "tag_groups": self.tag_group_list_ui,
        }

        super().__init__(parent)

        self.switch_page("tag_groups")

    def navigate_path(self, path: str):
        pass

    def get_page(self, page_name: str):
        """Get or create a page"""
        if page_name not in self._pages:
            creator = self._page_creators.get(page_name)
            if creator:
                self._pages[page_name] = creator()
                self.stack.addWidget(self._pages[page_name])
        return self._pages.get(page_name)

    def switch_page(self, page_name: str):
        # convert page_name to snake_case
        page_name = page_name.replace(' ', '_').lower()
        
        # Get or create the page and switch to it
        page = self.get_page(page_name)
        if page:
            self.stack.setCurrentWidget(page)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.stack = QStackedWidget(self)

        self.main_layout.addWidget(self.stack)

        self.setLayout(self.main_layout)

    def tag_group_list_ui(self) -> QWidget:
        widget = QWidget()
        base_layout = QVBoxLayout()
        widget.setLayout(base_layout)

        header_layout = QHBoxLayout()
        header_layout.addLayout(self._create_header("Tag Groups", font_size=14))
        header_layout.addStretch(1)
        new_btn = self._create_button("New", "Create a new tag group")
        new_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        header_layout.addWidget(new_btn)

        # Create the list widget
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        list_widget.setSizeAdjustPolicy(QListWidget.SizeAdjustPolicy.AdjustToContents)
        list_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        list_widget.setResizeMode(QListWidget.ResizeMode.Fixed)

        # Load the tag groups into the list widget
        for tag_group in self.db.tags.get_project_tags(self.active_project.id):
            item = TagGroupListWidget(tag_group, parent=list_widget)
            list_widget.addItem(item)
            list_widget.setItemWidget(item, item.widget)

        base_layout.addLayout(header_layout)
        base_layout.addWidget(list_widget)

        return widget