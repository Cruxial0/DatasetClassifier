import sys
from typing import List, Set
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QFileDialog, QScrollArea, 
                             QCheckBox, QSpacerItem, QSizePolicy, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QMimeData, QPoint, pyqtSignal
from PyQt6.QtGui import QDrag, QPalette, QColor
from pyqt6_multiselect_combobox import MultiSelectComboBox

from src.config_handler import ConfigHandler
from src.export import ExportRule

class RuleComponent(QWidget):
    deleteRequested = pyqtSignal(object)
    dragStarted = pyqtSignal(object)

    def __init__(self, categories: List[str], rule: ExportRule, editable: bool = True, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.rule = rule
        self.editable = editable

        self.priority_label = QLabel(str(self.rule.priority))

        self.combo_box = MultiSelectComboBox()
        self.combo_box.addItems(categories)
        self.combo_box.setDisplayDelimiter(", ")
        if editable:
            self.combo_box.setPlaceholderText("Select categories...")
        if self.rule.categories and editable:
            self.combo_box.setCurrentOptions(list(self.rule.categories))
        else:
            self.combo_box.setCurrentText("DEFAULT")
        self.combo_box.setEnabled(editable)

        self.file_path = QLineEdit(self.rule.destination)
        self.file_path.setPlaceholderText("File path...")
        self.file_path.setEnabled(editable)

        layout.addWidget(self.priority_label, 1)
        layout.addWidget(self.combo_box, 7)
        layout.addWidget(self.file_path, 2)

        if editable:
            self.delete_button = QPushButton("X")
            self.delete_button.clicked.connect(self.request_delete)
            layout.addWidget(self.delete_button)

        self.setLayout(layout)
        self.setAcceptDrops(True)

    def get_data(self):
        return ExportRule(
            categories=set(self.combo_box.currentData()),
            destination=self.file_path.text(),
            priority=int(self.priority_label.text())
        )

    def request_delete(self):
        self.deleteRequested.emit(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.editable:
            self.dragStarted.emit(self)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.editable:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(self.rule.priority))
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)

    def set_drag_highlight(self, highlight: bool):
        palette = self.palette()
        if highlight:
            palette.setColor(QPalette.ColorRole.Window, QColor(200, 200, 255))
        else:
            palette.setColor(QPalette.ColorRole.Window, self.parent().palette().color(QPalette.ColorRole.Window))
        self.setPalette(palette)
        self.setAutoFillBackground(highlight)

class ExportPopup(QWidget):
    def __init__(self, export_callback, categories, config: ConfigHandler):
        super().__init__()
        self.categories = categories
        self.export_callback = export_callback
        self.config = config
        self.initUI()
        self.drag_component = None

    def initUI(self):
        layout = QVBoxLayout()

        # Output directory selector
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        dir_button = QPushButton("Select output path")
        dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        layout.addLayout(dir_layout)

        # Add button
        add_button = QPushButton("Add Rule")
        add_button.clicked.connect(self.add_rule)
        layout.addWidget(add_button)

        # Scrollable area for category components
        self.scroll_area = QScrollArea()
        self.scroll_area.setContentsMargins(0,0,0,0)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.category_components = []

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        # Default rule (non-editable)
        default_rule = ExportRule(categories=None, destination='.', priority=0)
        self.add_rule_component(default_rule, editable=False)

        # Enable drag and drop for the layout
        self.scroll_widget.setAcceptDrops(True)

        # Checkboxes
        check_layout = QHBoxLayout()
        self.checkboxes = {}
        preset, scores = self.config.get_scores()
        for name, label in scores.items():
            checkbox = QCheckBox(label)
            checkbox.setObjectName(name)
            self.checkboxes[name] = checkbox
            check_layout.addWidget(checkbox)
        layout.addLayout(check_layout)

        options_layout = QHBoxLayout()
        self.export_captions = QCheckBox('Export Captions')
        self.seperate_by_score = QCheckBox('Seperate by score')
        self.export_captions.setChecked(self.config.get_export_option('export_captions'))
        self.seperate_by_score.setChecked(self.config.get_export_option('seperate_by_score'))
        options_layout.addWidget(self.export_captions)
        options_layout.addWidget(self.seperate_by_score)
        layout.addLayout(options_layout)

        # Buttons
        button_layout = QHBoxLayout()
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.export_data)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(export_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle('Export Rules')
        self.setGeometry(300, 300, 600, 400)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.dir_input.setText(directory)

    def add_rule(self):
        new_rule = ExportRule(categories=set(), destination='', priority=len(self.category_components))
        self.add_rule_component(new_rule)

    def add_rule_component(self, rule: ExportRule, editable: bool = True):
        component = RuleComponent(self.categories, rule, editable, parent=self.scroll_widget)
        component.deleteRequested.connect(self.delete_rule)
        component.dragStarted.connect(self.drag_started)
        self.category_components.insert(0, component)
        self.scroll_layout.insertWidget(0, component)
        self.update_priorities()

    def delete_rule(self, component):
        if component.rule.priority != 0:  # Prevent deleting the default rule
            self.scroll_layout.removeWidget(component)
            component.deleteLater()
            self.category_components.remove(component)
            self.update_priorities()

    def update_priorities(self):
        for i, component in enumerate(reversed(self.category_components)):
            component.rule.priority = i
            component.priority_label.setText(str(i))

    def export_data(self):
        data = {
            'output_directory': self.dir_input.text(),
            'rules': [component.get_data() for component in reversed(self.category_components)],
            'scores': [name for name, checkbox in self.checkboxes.items() if checkbox.isChecked()],
            'seperate_by_score': self.seperate_by_score.isChecked(),
            'export_captions': self.export_captions.isChecked()
        }
        if data['output_directory'] == '':
            QMessageBox.warning(self, 'Invalid export', 'Select an output path before exporting')
            return
        if len(data['scores']) < 1:
            QMessageBox.warning(self, 'Invalid export', 'Select at least one score before exporting')
            return
        self.export_callback(data)
        self.close()

    def drag_started(self, component):
        self.drag_component = component

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and self.drag_component and self.drag_component.editable:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and self.drag_component and self.drag_component.editable:
            event.accept()
            self.update_drag_highlight(event.position().toPoint())
        else:
            event.ignore()

    def update_drag_highlight(self, position):
        for component in self.category_components:
            if component.editable:
                highlight = component.geometry().contains(position) and component != self.drag_component
                component.set_drag_highlight(highlight)

    def dropEvent(self, event):
        if not (event.mimeData().hasText() and self.drag_component and self.drag_component.editable):
            event.ignore()
            return

        drop_position = event.position().toPoint()
        target_component = None

        for component in self.category_components:
            if component.editable and component.geometry().contains(drop_position):
                target_component = component
                break

        if target_component and target_component != self.drag_component:
            source_index = self.category_components.index(self.drag_component)
            target_index = self.category_components.index(target_component)

            # Reorder the components list
            self.category_components.insert(target_index, self.category_components.pop(source_index))

            # Clear layout and re-add components in new order
            for i in reversed(range(self.scroll_layout.count())):
                widget = self.scroll_layout.itemAt(i).widget()
                if widget is not None:
                    self.scroll_layout.removeWidget(widget)

            for component in self.category_components:
                self.scroll_layout.addWidget(component)

            self.update_priorities()

        # Reset drag highlight
        for component in self.category_components:
            component.set_drag_highlight(False)

        self.drag_component = None
        event.accept()

    def dragLeaveEvent(self, event):
        for component in self.category_components:
            component.set_drag_highlight(False)