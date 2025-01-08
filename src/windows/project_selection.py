from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QListWidget, QListWidgetItem, QLabel
)
from PyQt6.QtCore import Qt


from src.config_handler import ConfigHandler
from src.project_utils import load_project_from_id
from src.project import Project
from src.database.database import Database
from src.utils import get_time_ago
from src.popups.new_project_popup import NewProjectPopup
from src.popups.migrate_project_popup import MigrateProjectPopup
from src.windows.dataset_classifier import DatasetClassifier
from src.styling.style_manager import StyleManager

class ProjectListItem(QListWidgetItem):
    def __init__(self, id: int, name: str, last_updated: str):
        # Format the display text with name and date aligned
        display_text = f"{name:<30} {last_updated}"
        super().__init__(display_text)
        
        # Store the original data
        self.id = id
        self.project_name = name
        self.last_updated = last_updated

class ProjectListWidget(QWidget):
    def __init__(self, database: Database, style_manager: StyleManager):
        super().__init__()
        self.db = database
        self.style_manager = style_manager
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(self.style_manager.get_stylesheet(QListWidget))
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        
        # Use a monospace font to ensure proper alignment
        font = self.list_widget.font()
        font.setFamily("Monospace")
        self.list_widget.setFont(font)
        
        # Populate list with sample data
        self.populate_list()
        
        # Connect selection signal
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.list_widget)

    def populate_list(self):
        # Replace this with actual data from your database
        data = self.db.projects.load_projects_by_date()
        
        for id, name, _, date in data:
            item = ProjectListItem(id, name, get_time_ago(date))
            self.list_widget.addItem(item)

    def on_selection_changed(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            self.selected_item = selected_items[0]

class ProjectSelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.config_handler = ConfigHandler()
        self.style_manager = StyleManager(self.config_handler)

        self.setStyleSheet(self.style_manager.get_stylesheet(QMainWindow))

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Project Selection")
        self.setGeometry(100, 100, 800, 400)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left column - Buttons
        left_column = QVBoxLayout()

        welcome_label = QLabel("Welcome!")
        welcome_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        welcome_label.setMargin(10)
        left_column.addWidget(welcome_label)
        
        functions_layout = QVBoxLayout()
        functions_layout.setContentsMargins(7, 0, 7, 0)
        left_column.addLayout(functions_layout)

        new_project_btn = QPushButton("New Project")
        new_project_btn.setWhatsThis("Create a new project")
        new_project_btn.setToolTip("Create a new project")
        new_project_btn.setStyleSheet(self.style_manager.get_stylesheet(QPushButton))
        new_project_btn.clicked.connect(self.on_new_project)
        
        import_legacy_btn = QPushButton("Import Legacy Database")
        import_legacy_btn.setStyleSheet(self.style_manager.get_stylesheet(QPushButton))
        import_legacy_btn.clicked.connect(self.on_import_legacy)
        
        functions_layout.addWidget(new_project_btn)
        functions_layout.addWidget(import_legacy_btn)
        left_column.addStretch()
        
        # Right column - Recent Projects
        right_column = QVBoxLayout()

        project_list_label = QLabel("Recent Projects")
        project_list_label.setStyleSheet(self.style_manager.get_stylesheet(QLabel))
        project_list_label.setMargin(10)
        right_column.addWidget(project_list_label)

        self.project_list_widget = ProjectListWidget(self.db, self.style_manager)
        right_column.addWidget(self.project_list_widget)

        # Add buttons to right column
        buttons_layout = QHBoxLayout()
        
        # add 10px margin
        buttons_layout.setContentsMargins(10, 0, 10, 10)

        open_button = QPushButton("Open")
        delete_button = QPushButton("Delete", enabled=False)
        edit_button = QPushButton("Edit", enabled=False)

        open_button.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'accent'))
        delete_button.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'warning'))
        edit_button.setStyleSheet(self.style_manager.get_stylesheet(QPushButton))

        open_button.clicked.connect(self.open_project)
        # delete_button.clicked.connect(self.delete_project)
        # edit_button.clicked.connect(self.edit_project)

        buttons_layout.addWidget(open_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)

        right_column.addLayout(buttons_layout)

        # Add columns to main layout
        main_layout.addLayout(left_column)
        main_layout.addLayout(right_column)
        
        # Set the ratio between columns (1:2)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 2)

    def on_new_project(self):
        popup = NewProjectPopup(self.db)
        popup.show()
        popup.set_callback(self.new_project_created)

    def new_project_created(self, project: Project):
        app = DatasetClassifier(self.db, project)
        app.show()
        self.close()

    def on_import_legacy(self):
        popup = MigrateProjectPopup(self.db)
        popup.show()
        popup.set_callback(self.project_migrated)

    def open_project(self):
        if self.project_list_widget is None or hasattr(self.project_list_widget, 'selected_item') is False:
            return
        if self.project_list_widget.selected_item:
            project = load_project_from_id(self.project_list_widget.selected_item.id, self.db)
            app = DatasetClassifier(self.db, project)
            app.show()
            self.close()

    def project_migrated(self, project: Project):
        app = DatasetClassifier(self.db, project)
        app.show()
        self.close()