from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QFileDialog

from src.project_manager import Project

class NewProjectPopup(QWidget):
    def __init__(self):
        super().__init__()
        self.callback = None
        self.projectName = None
        self.directories = []
        self.createUI()
        self.update_create_enabled()

    def createUI(self):
        self.setWindowTitle("New Project")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)

        # Project name
        input_layout = QHBoxLayout()
        input_label = QLineEdit()
        input_label.setPlaceholderText("Project Name")
        input_label.textChanged.connect(lambda text: self.update_project_name(text))
        input_layout.addWidget(input_label)

        # Directories
        directories_layout = QHBoxLayout()
        self.directories_list = QListWidget()
        directories_layout.addWidget(self.directories_list)

        # + and - buttons
        dir_buttons_layout = QVBoxLayout()
        add_button = QPushButton("+")
        add_button.setFixedWidth(30)
        remove_button = QPushButton("-")
        remove_button.setFixedWidth(30)
        dir_buttons_layout.addWidget(add_button)
        dir_buttons_layout.addWidget(remove_button)
        directories_layout.addLayout(dir_buttons_layout)

        # Connect buttons to slots
        add_button.clicked.connect(self.add_directory)
        remove_button.clicked.connect(self.remove_directory)

        layout.addLayout(input_layout)
        layout.addLayout(directories_layout)

        # Spacer
        layout.addStretch(1)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_project)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)

        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

    def set_callback(self, callback) -> Project:
        self.callback = callback

    def create_project(self) -> Project:
        project = Project(self.projectName, self.directories)
        self.callback(project)
        self.close()

    def update_directories(self):
        self.directories = [self.directories_list.item(i).text() for i in range(self.directories_list.count())]
        self.update_create_enabled()

    def add_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directories_list.addItem(directory)
        
        self.update_directories()
            
    def remove_directory(self):
        current_item = self.directories_list.currentItem()
        if current_item:
            self.directories_list.takeItem(self.directories_list.row(current_item))

        self.update_directories()

    def update_project_name(self, name: str) -> None:
        self.projectName = name
        self.update_create_enabled()

    def update_create_enabled(self) -> None:
        if self.projectName and self.directories:
            self.create_button.setEnabled(True)
        else:
            self.create_button.setEnabled(False)