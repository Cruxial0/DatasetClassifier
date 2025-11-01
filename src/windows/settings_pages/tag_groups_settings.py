import random
from typing import Literal
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget, QListWidget, QSizePolicy, QMessageBox
from src.windows.settings_pages.settings_widget import SettingsWidget
from src.widgets.tag_group_list_widget import TagGroupListWidget
from src.tagging.tag_group import Tag, TagGroup
from src.windows.settings_pages.tag_group_pages.tag_group_add_edit import TagGroupAddOrEditPage
from src.windows.settings_pages.tag_group_pages.tags_page import TagListPage
from src.windows.settings_pages.tag_group_pages.tag_conditionals import TagConditionalsPage
from src.styling.styling_utils import styled_question_box

class TagGroupSettings(SettingsWidget):
    def __init__(self, parent=None):
        
        self._pages = {}
        self._page_creators = {
            "tag_groups": self.tag_group_list_ui,
            "add_or_edit_tag_group": lambda **kwargs: TagGroupAddOrEditPage(self, **kwargs),
            "tag_page": lambda **kwargs: TagListPage(self, **kwargs),
            "conditionals": lambda **kwargs: TagConditionalsPage(self, **kwargs),
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
        self.list_widget.setStyleSheet(self.style_manager.get_stylesheet(QListWidget))
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.setSizeAdjustPolicy(QListWidget.SizeAdjustPolicy.AdjustToContents)
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Fixed)
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.list_widget.model().rowsMoved.connect(self.on_tag_groups_reordered)
        
        base_layout.addLayout(header_layout)
        base_layout.addWidget(self.list_widget)

        return widget
    
    def list_item_button_clicked(self, btn: Literal['edit', 'tags', 'activation', 'delete'], tag_group: TagGroup):
        if btn == 'edit':
            self.switch_page("add_or_edit_tag_group")
            edit_page: TagGroupAddOrEditPage = self.stack.currentWidget()
            edit_page.set_mode('edit')
            edit_page.set_group(tag_group)
        elif btn == "tags":
            self.switch_page("tag_page", tag_group=tag_group)
            tag_page: TagListPage = self.stack.currentWidget()
            tag_page.set_group(tag_group)
        elif btn == "activation":
            self.switch_page("conditionals", tag_group=tag_group)
            cond_page: TagConditionalsPage = self.stack.currentWidget()
            cond_page.set_group(tag_group)
        elif btn == "delete":
            self._delete_tag_group(tag_group)

    def _populate_tag_groups(self):
        for tag_group in self.tag_groups:
            tag_group.verify_self()
            item = TagGroupListWidget(tag_group, self.style_manager, callback=self.list_item_button_clicked, parent=self.list_widget)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item.widget)

    def open_new_tag_group(self):
        self.switch_page("add_or_edit_tag_group")
        edit_page: TagGroupAddOrEditPage = self.stack.currentWidget()
        edit_page.set_mode('add')

    def save_tag_group(self, tag_group: TagGroup, switch_page: bool = True):
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
            self.add_new_tag_group(tag_group)
        else:
            self.db.tags.update_tag_group(tag_group)
            self.update_list_item(tag_group)
            self.select_by_group(tag_group)

        if switch_page:
            self.switch_page("tag_groups")

    def add_new_tag_group(self, tag_group: TagGroup):
        
        # id, project_id and order are expected to be -1
        tag_group.project_id = self.active_project.id
        tag_group.order = len(self.tag_groups)

        id = self.db.tags.add_tag_group(tag_group.name, tag_group.order, tag_group.project_id)
        tag_group.id = id

        # Ensure all values are committed
        self.db.tags.update_tag_group(tag_group)

        self.tag_groups.append(tag_group)

        item = TagGroupListWidget(tag_group, self.style_manager, callback=self.list_item_button_clicked, parent=self.list_widget)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item.widget)

        self.list_widget.setCurrentItem(item)

    def add_tag(self, group_id: int, tag: Tag):
        group = self._group_from_id(group_id)
        group.tags.append(tag)
        self.db.tags.add_tag(tag.name, group_id, tag.display_order)

    def delete_tag(self, tag_id: int):
        self.db.tags.delete_tag(tag_id)

    def rename_tag(self, group_id: int, tag_id: int, new_name: str):
        group = self._group_from_id(group_id)
        tag = group.get_tag(tag_id)
        tag.name = new_name
        self.db.tags.update_tag(tag)
        self.update_list_item(group)

    def update_list_item(self, tag_group: TagGroup):
        for i in range(self.list_widget.count()):
            item: TagGroupListWidget = self.list_widget.item(i)
            if item.tag_group.id == tag_group.id:
                item.update_group(tag_group)
                break

    def select_by_group(self, tag_group: TagGroup):
        for i in range(self.list_widget.count()):
            item: TagGroupListWidget = self.list_widget.item(i)
            if item.tag_group.id == tag_group.id:
                self.list_widget.setCurrentItem(item)
                break

    def update_tag_order(self, order: list[tuple[int, int]]):
        self.db.tags.update_tag_order(order)

    def update_tag_group_order(self, order: list[tuple[int, int]]):
        self.db.tags.update_tag_group_order(order)

    def on_tag_groups_reordered(self):
        reorder_data = []
        # Iterate through all items in the list
        for i in range(self.list_widget.count()):
            item: TagGroupListWidget = self.list_widget.item(i)
            group = item.tag_group

            # Create tuple of (tag_id, new_display_order)
            reorder_data.append((group.id, i))

            # Update the tag's display_order attribute
            group.display_order = i

        self.update_tag_group_order(reorder_data)
            

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

    def _delete_tag_group(self, group: TagGroup):
        """Opens a confirmation dialog to delete a tag group and it's corresponding UI element and deletes them if confirmed."""
        dialog = styled_question_box(
            self,
            "Delete tag group",
            f"Are you sure you want to delete the tag group '{group.name}'?\nThis action cannot be undone.",
            self.style_manager,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No)

        if dialog == QMessageBox.StandardButton.Yes:
            self.db.tags.delete_tag_group(group.id)
            self.tag_groups.remove(group)
            ui_item = self._ui_element_from_group(group)
            if ui_item:
                self.list_widget.takeItem(self.list_widget.row(ui_item))

    def _group_from_id(self, group_id: int):
        for group in self.tag_groups:
            if group.id == group_id:
                return group
            
    def _ui_element_from_group(self, group: TagGroup):
        for i in range(self.list_widget.count()):
            item: TagGroupListWidget = self.list_widget.item(i)
            if item.tag_group.id == group.id:
                return item

    def _handle_first_load(self, page_name: str, **kwargs):
        if page_name == "add_or_edit_tag_group":
            edit_page: TagGroupAddOrEditPage = self._pages.get(page_name)
            edit_page.onCancel.connect(lambda: self.switch_page("tag_groups"))
            edit_page.onSave.connect(self.save_tag_group)
            edit_page.onCreate.connect(self.save_tag_group)

        elif page_name == "tag_page":
            tag_page: TagListPage = self._pages.get(page_name)
            tag_page.doneClicked.connect(lambda: self.switch_page("tag_groups"))
            tag_page.tagAdded.connect(self.add_tag)
            tag_page.tagDeleted.connect(self.delete_tag)
            tag_page.tagRenamed.connect(self.rename_tag)
            tag_page.tagsReordered.connect(self.update_tag_order)

        elif page_name == "conditionals":
            cond_page: TagConditionalsPage = self._pages.get(page_name)
            cond_page.cancelClicked.connect(lambda: self.switch_page("tag_groups"))
            cond_page.conditionSaved.connect(self.save_tag_group)