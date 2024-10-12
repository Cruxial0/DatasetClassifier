import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QFileDialog, QScrollArea, 
                             QCheckBox, QSpacerItem, QSizePolicy)

class CategoryComponent(QWidget):
    def __init__(self, name,  parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.category_button = QPushButton(name)
        self.category_button.setCheckable(True)
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("File path...")
        layout.addWidget(self.category_button)
        layout.addWidget(self.file_path)
        self.setLayout(layout)

    def get_data(self):
        return {
            'category': self.category_button.isChecked(),
            'file_path': self.file_path.text()
        }

class ExportPopup(QWidget):
    def __init__(self, export_callback, categories):
        super().__init__()
        self.categories = categories
        self.export_callback = export_callback
        self.initUI()

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

        # Scrollable area for category components
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0,0,0,0)
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setSpacing(10)  # Set fixed spacing between items
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)  # Set margins around the entire layout
        self.category_components = []
        for i in range(len(self.categories)):
            component = CategoryComponent(self.categories[i][0].text())
            self.category_components.append(component)
            self.scroll_layout.addWidget(component)
            if _ < 9:
                self.scroll_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Checkboxes
        check_layout = QHBoxLayout()
        self.checkboxes = {}
        labels = ['score_9', 'score_8_up', 'score_7_up', 'score_6_up', 'score_5_up', 'score_4_up', 'discard']
        for label in labels:
            checkbox = QCheckBox(label)
            self.checkboxes[label] = checkbox
            check_layout.addWidget(checkbox)
        layout.addLayout(check_layout)

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
        self.setWindowTitle('Popup Window')
        self.setGeometry(300, 300, 400, 400)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.dir_input.setText(directory)

    def export_data(self):
        data = {
            'output_directory': self.dir_input.text(),
            'categories': [component.get_data() for component in self.category_components],
            'checkboxes': {label: checkbox.isChecked() for label, checkbox in self.checkboxes.items()}
        }
        self.export_callback(data)
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExportPopup()
    ex.show()
    sys.exit(app.exec())