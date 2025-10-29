from typing import List
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QListWidget, QListWidgetItem, QPushButton, 
                            QWidget, QLabel)
from PyQt6.QtCore import pyqtSignal
from src.windows.settings_pages.settings_widget import SettingsWidget
from src.tagging.tag_group import Tag, TagGroup
from src.widgets.tag_widget import TagListItem

class TagListPage(SettingsWidget):
    tagsReordered = pyqtSignal(list)
    tagAdded = pyqtSignal(int, Tag)
    tagRenamed = pyqtSignal(TagGroup, int, str)
    tagDeleted = pyqtSignal(int)
    doneClicked = pyqtSignal()
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.selected_group: TagGroup = kwargs.get('tag_group', None)
        self.selected_element: TagListItem = None
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Input area
        input_layout = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setStyleSheet(self.style_manager.get_stylesheet(QLineEdit))
        self.tag_input.setPlaceholderText("Add new tag")
        self.tag_input.returnPressed.connect(self.add_tag)
        
        add_button = QPushButton("Add")
        add_button.setStyleSheet(self.style_manager.get_stylesheet(QPushButton))
        add_button.clicked.connect(self.add_tag)
        
        input_layout.addWidget(self.tag_input)
        input_layout.addWidget(add_button)
        layout.addLayout(input_layout)
        
        # Tags list
        self.tags_list = QListWidget()
        self.tags_list.setStyleSheet(self.style_manager.get_stylesheet(QListWidget))
        self.tags_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.tags_list.model().rowsMoved.connect(self.on_tags_reordered)
        self.tags_list.itemClicked.connect(self.item_clicked)
        layout.addWidget(self.tags_list)
        
        # Done button
        done_button = QPushButton("Done")
        done_button.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'accept'))
        done_button.clicked.connect(self.doneClicked)
        layout.addWidget(done_button)
        
    def set_group(self, group):
        self.selected_group = group
        self.refresh_tags()
        
    def refresh_tags(self):
        self.tags_list.clear()
        if self.selected_group and self.selected_group.tags:
            for tag in sorted(self.selected_group.tags, key=lambda x: x.display_order):
                self.create_tag_item(tag)
                
    def create_tag_item(self, tag: Tag) -> QListWidgetItem:
        item = QListWidgetItem()
        widget = TagListItem(tag, self.style_manager, self.tags_list)
        
        self._assign_signals(widget)

        self.tags_list.addItem(item)
        self.tags_list.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())
        
        return widget
    
    def _assign_signals(self, item: TagListItem):
        item.focused.connect(self.set_list_item_focus)
        item.tagRenamed.connect(self.rename_tag)
        item.deleteClicked.connect(self.delete_tag)

    def add_tag(self):
        tag = Tag(-1, self.tag_input.text(), self.tags_list.count())
        if tag and self.selected_group:
            self.create_tag_item(tag)
            self.selected_group.tags.append(tag)
            self.tag_input.clear()
            self.tagAdded.emit(self.selected_group.id, tag)
            
    def delete_tag(self, tag_id: int):
        self.tagDeleted.emit(tag_id)

        if self.selected_group:
            for tag in self.selected_group.tags:
                if tag.id == tag_id:
                    self.selected_group.tags.remove(tag)
                    break

        self.refresh_tags()

    def rename_tag(self, tag_id: int, new_name: str):
        if self.selected_group:
            self.tagRenamed.emit(self.selected_group, tag_id, new_name)
        else:
            print("Could not rename tag: no selected group")
            
    def on_tags_reordered(self):
        if self.selected_group:
            reorder_data = []
            # Iterate through all items in the list
            for i in range(self.tags_list.count()):
                item = self.tags_list.item(i)
                widget: TagListItem = self.tags_list.itemWidget(item)
                tag = widget.tag

                # Create tuple of (tag_id, new_display_order)
                reorder_data.append((tag.id, i))

                # Update the tag's display_order attribute
                tag.display_order = i
                widget.set_index_label(i)
                
            # Emit the signal with the reorder data
            self.tagsReordered.emit(reorder_data)
            
    def set_list_item_focus(self, item: QWidget):
        for i in range(self.tags_list.count()):
            if self.tags_list.itemWidget(self.tags_list.item(i)) == item:
                self.tags_list.setCurrentRow(i)

                if self.selected_element:
                    self.selected_element.reset_state()

                self.selected_element = self.tags_list.itemWidget(self.tags_list.item(i))
                break
    
    def item_clicked(self, item: QListWidgetItem):
        self.selected_element = self.tags_list.itemWidget(item)
        self.list_item_clicked = True

    def navigate_path(self, path: str):
        pass