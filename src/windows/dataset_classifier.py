from PyQt6.QtWidgets import (QHBoxLayout, QMainWindow, QWidget, QStackedWidget)
from src.pages.tagging_page import TaggingPage
from src.pages.scoring_page import ScoringPage
from src.project_utils import load_project_from_id
from src.database.database import Database
from src.project import Project
from src.button_states import ButtonStateManager
from src.config_handler import ConfigHandler
from src.ui_components import UIComponents
from src.popups.export_popup import ExportPopup
from src.windows.settings_window import SettingsWindow
from src.popups.new_project_popup import NewProjectPopup
from src.popups.migrate_project_popup import MigrateProjectPopup
from src.update_poller import UpdatePoller

# dataset_classifier.py
class DatasetClassifier(QMainWindow):
    def __init__(self, database: Database, project: Project):
        super().__init__()
        self.active_project = project
        self.db = database
        self.config_handler = ConfigHandler()
        self.button_states = ButtonStateManager()
        self.update_poller = UpdatePoller()
        self.current_mode = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dataset Classifier')
        self.setGeometry(100, 100, 1000, 600)
        
        # Create and set the stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize pages
        self.scoring_page = ScoringPage(self)
        self.tagging_page = TaggingPage(self)
        
        # Add both pages to the stacked widget
        self.stacked_widget.addWidget(self.scoring_page)
        self.stacked_widget.addWidget(self.tagging_page) 

        # Create menu bar
        self.create_menu_bar()
        
        # Set initial project
        self.scoring_page.set_active_project(self.active_project)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        project_menu = menu_bar.addMenu('Project')
        view_menu = menu_bar.addMenu('View')
        options_menu = menu_bar.addMenu('Options')

        file_menu.setToolTipsVisible(True)
        project_menu.setToolTipsVisible(True)
        view_menu.setToolTipsVisible(True)
        options_menu.setToolTipsVisible(True)

        actions = UIComponents.create_menu_actions(self.config_handler)
        self.hide_scored_action, self.treat_categories_as_scoring_action, self.auto_scroll_on_scoring_action, self.export_action, self.write_to_filesystem_action, self.settings_action, self.project_new_action, self.project_edit_action, self.project_migrate_action, self.menu_button = actions  

        button_widget = QWidget()
        layout = QHBoxLayout(button_widget)
        layout.addStretch()  # This pushes the button to the right
        layout.addWidget(self.menu_button)
        layout.setContentsMargins(0, 7, 7, 0)  
        menu_bar.setCornerWidget(button_widget)

        file_menu.addAction(self.export_action)
        file_menu.addAction(self.settings_action)
        project_menu.addAction(self.project_new_action)
        project_menu.addAction(self.project_edit_action)
        project_menu.addAction(self.project_migrate_action)
        view_menu.addAction(self.hide_scored_action)
        # options_menu.addAction(self.treat_categories_as_scoring_action)
        options_menu.addAction(self.auto_scroll_on_scoring_action)
        options_menu.addAction(self.write_to_filesystem_action)
        self.menu_button.clicked.connect(self.switch_mode)

        
        # self.hide_scored_action.triggered.connect(self.toggle_hide_scored_images)
        # self.treat_categories_as_scoring_action.triggered.connect(self.toggle_treat_categories_as_scoring)
        # self.auto_scroll_on_scoring_action.triggered.connect(self.toggle_auto_scroll_on_scoring)
        # self.write_to_filesystem_action.triggered.connect(self.toggle_write_to_filesystem)
        # self.export_action.triggered.connect(self.open_export_window)
        self.settings_action.triggered.connect(self.open_settings_window)
        # self.project_new_action.triggered.connect(self.new_project)
        # self.project_migrate_action.triggered.connect(self.migrate_project)

    def setup_stacked_widget(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize modes
        self.scoring_mode = ScoringPage(self)
        self.tagging_mode = TaggingPage(self)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(self.scoring_mode)
        self.stacked_widget.addWidget(self.tagging_mode)

        self.stackedLayout.addWidget(self.stacked_widget)

    def switch_mode(self):
        self.current_mode = 1 if self.current_mode == 0 else 0
        self.stacked_widget.setCurrentIndex(self.current_mode)

    def handle_project_loaded(self, project: Project):
        """Called when a project is loaded"""
        self.active_project = project
        self.scoring_page.set_active_project(project)
        # Enable relevant UI elements
        self.export_action.setEnabled(True)
        self.settings_action.setEnabled(True)

    def apply_keybindings(self):
        """Update keybindings across all pages"""
        self.scoring_page.apply_keybindings()

    def update_scoring_buttons(self):
        """Update scoring button states across all pages"""
        self.scoring_page.update_scoring_buttons()

    def update_button_colors(self):
        """Update button colors across all pages"""
        self.scoring_page.update_button_colors()

    def open_settings_window(self, page: str = None):
        settings_window = SettingsWindow(self.config_handler, self, page)
        settings_window.show()