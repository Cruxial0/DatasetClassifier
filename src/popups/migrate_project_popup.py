import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QFileDialog

from src.database.database import Database
from src.project import Project
from src.project_utils import from_legacy_database

class MigrateProjectPopup(QWidget):
    def __init__(self, database: Database):
        super().__init__()
        self.callback = None
        self.projectName = None
        self.filePath = None
        self.database = database
        self.createUI()
        self.update_migrate_enabled()

    def createUI(self):
        self.setWindowTitle("Migrate Project")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)

        # Project name
        input_layout = QHBoxLayout()
        input_label = QLineEdit()
        input_label.setPlaceholderText("Project Name")
        input_label.textChanged.connect(lambda text: self.update_project_name(text))
        input_layout.addWidget(input_label)

        # SQLite selector
        sqlite_layout = QHBoxLayout()
        self.sqlite_input = QLineEdit()
        self.sqlite_input.setReadOnly(True)
        self.sqlite_input.setPlaceholderText("Legacy SQLite file")
        self.sqlite_input.textChanged.connect(lambda text: self.update_migrate_enabled())
        sqlite_layout.addWidget(self.sqlite_input)

        self.sqlite_button = QPushButton("Select")
        self.sqlite_button.clicked.connect(self.select_sqlite)
        sqlite_layout.addWidget(self.sqlite_button)

        layout.addLayout(input_layout)
        layout.addLayout(sqlite_layout)

        # Spacer
        layout.addStretch(1)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.migrate_button = QPushButton("Migrate")
        self.migrate_button.clicked.connect(self.migrate_project)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)

        buttons_layout.addWidget(self.migrate_button)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

    def set_callback(self, callback) -> Project:
        self.callback = callback

    def migrate_project(self) -> Project:
        project = from_legacy_database(self.projectName, self.filePath, self.database)
        self.callback(project)
        self.close()

    def update_directories(self):
        self.directories = [self.directories_list.item(i).text() for i in range(self.directories_list.count())]
        self.update_migrate_enabled()

    def select_sqlite(self):
        print("Selecting SQLite file...")
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("SQLite files (*.sqlite *.db *.sqlite3)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        if dialog.exec():
            self.filePath = dialog.selectedFiles()[0]
            self.sqlite_input.setText(self.filePath)

    def update_project_name(self, name: str) -> None:
        self.projectName = name
        self.update_migrate_enabled()

    def update_migrate_enabled(self) -> None:
        if self.projectName and self.filePath:
            if os.path.exists(self.filePath):
                self.migrate_button.setEnabled(True)
            else:
                self.migrate_button.setEnabled(False)