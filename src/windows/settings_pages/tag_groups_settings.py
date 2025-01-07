import random
from typing import Literal
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget, QListWidget, QSizePolicy
from src.windows.settings_pages.settings_widget import SettingsWidget
from src.widgets.tag_group_list_widget import TagGroupListWidget
from src.tagging.tag_group import TagGroup
from src.windows.settings_pages.tag_group_pages.tag_group_add_edit import TagGroupAddOrEditPage

class TagGroupSettings(SettingsWidget):
    def __init__(self, parent=None):
        
        self._pages = {}
        self._page_creators = {
            "tag_groups": self.tag_group_list_ui,
            "add_or_edit_tag_group": lambda **kwargs: TagGroupAddOrEditPage(self, **kwargs),
        }

        super().__init__(parent)

        self.switch_page("tag_groups")

        self.tag_groups = self.db.tags.get_project_tags(self.active_project.id)
        self._populate_tag_groups()

    def navigate_path(self, path: str):
        pass

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
        new_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        new_btn.clicked.connect(self.open_new_tag_group)
        header_layout.addWidget(new_btn)

        # Create the list widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.setSizeAdjustPolicy(QListWidget.SizeAdjustPolicy.AdjustToContents)
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Fixed)
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        
        base_layout.addLayout(header_layout)
        base_layout.addWidget(self.list_widget)

        return widget
    
    def _populate_tag_groups(self):
        def list_item_button_clicked(btn: Literal['edit', 'tags', 'activation'], tag_group: TagGroup):
            if btn == 'edit':
                self.switch_page("add_or_edit_tag_group")
                edit_page: TagGroupAddOrEditPage = self.stack.currentWidget()
                edit_page.set_mode('edit')
                edit_page.set_group(tag_group)
            elif btn == "tags":
                self.switch_page("tag_groups", tag_group=tag_group)
            elif btn == "activation":
                self.switch_page("tag_groups", tag_group=tag_group)

        for tag_group in self.tag_groups:
            item = TagGroupListWidget(tag_group, callback=list_item_button_clicked, parent=self.list_widget)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item.widget)

    def open_new_tag_group(self):
        self.switch_page("add_or_edit_tag_group")
        edit_page: TagGroupAddOrEditPage = self.stack.currentWidget()
        edit_page.set_mode('add')

    def save_tag_group(self, tag_group: TagGroup):
        """
        Saves a tag group to the database. If the tag group already exists in
        `self.tag_groups`, it is replaced with the given tag group. Otherwise, it
        is added to the list.

        Args:
            tag_group (TagGroup): The tag group to save.
        """
        exists = False
        for tg in self.tag_groups:
            if tg.id == tag_group.id:
                tg = tag_group
                exists = True
                break

        if not exists:
            self.tag_groups.append(tag_group)

        self.db.tags.update_tag_group(tag_group)

    # Page navigation
    def get_page(self, page_name: str, **kwargs):
        """Get or create a page"""
        if page_name not in self._pages:
            creator = self._page_creators.get(page_name)
            if creator:
                self._pages[page_name] = creator(**kwargs)
                self.stack.addWidget(self._pages[page_name])
                self._handle_first_load(page_name, **kwargs)
        return self._pages.get(page_name)

    def switch_page(self, page_name: str, **kwargs):
        # convert page_name to snake_case
        page_name = page_name.replace(' ', '_').lower()
        
        # Get or create the page and switch to it
        page = self.get_page(page_name, **kwargs)
        if page:
            self.stack.setCurrentWidget(page)

    def _handle_first_load(self, page_name: str, **kwargs):
        if page_name == "add_or_edit_tag_group":
            edit_page: TagGroupAddOrEditPage = self._pages.get(page_name)
            edit_page.cancelled.connect(lambda: self.switch_page("tag_groups"))
            edit_page.onSave.connect(self.save_tag_group)
