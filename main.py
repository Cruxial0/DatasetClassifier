import os
from pathlib import Path
import subprocess
import sys
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QMainWindow, QApplication, QWidget, QLabel, QStackedWidget)
from PyQt6.QtGui import QKeySequence, QShortcut, QTransform
from PyQt6.QtCore import Qt, QTimer
from src.pages.scoring_page import ScoringPage
from src.project_utils import load_project_from_id
from src.database.database import Database
from src.project import Project
from src.export import ExportRule, Exporter
from src.button_states import ButtonStateManager
from src.database.database_legacy import LegacyDatabase
from src.config_handler import ConfigHandler
from src.ui_components import UIComponents
from src.image_handler import ImageHandler
from src.utils import key_to_unicode
from src.theme import set_dark_mode
from src.windows.export_popup import ExportPopup
from src.windows.settings_window import SettingsWindow
from src.windows.new_project_popup import NewProjectPopup
from src.windows.migrate_project_popup import MigrateProjectPopup

# dataset_classifier.py
class DatasetClassifier(QMainWindow):
    def __init__(self):
        super().__init__()
        self.active_project = None
        self.db = Database()
        self.config_handler = ConfigHandler()
        self.button_states = ButtonStateManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dataset Classifier')
        self.setGeometry(100, 100, 1000, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Setup UI components
        self.create_menu_bar()
        # main_layout.addLayout(self.create_project_selection())
        
        # Setup stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize pages
        self.scoring_page = ScoringPage(self)
        self.stacked_widget.addWidget(self.scoring_page)
        
        # Setup mode switching
        self.setup_mode_switching()

        project = load_project_from_id(1, self.db)
        self.scoring_page.set_active_project(project)

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
        self.hide_scored_action, self.treat_categories_as_scoring_action, self.auto_scroll_on_scoring_action, self.export_action, self.write_to_filesystem_action, self.settings_action, self.project_new_action, self.project_edit_action, self.project_migrate_action = actions  

        file_menu.addAction(self.export_action)
        file_menu.addAction(self.settings_action)
        project_menu.addAction(self.project_new_action)
        project_menu.addAction(self.project_edit_action)
        project_menu.addAction(self.project_migrate_action)
        view_menu.addAction(self.hide_scored_action)
        # options_menu.addAction(self.treat_categories_as_scoring_action)
        options_menu.addAction(self.auto_scroll_on_scoring_action)
        options_menu.addAction(self.write_to_filesystem_action)

        # self.hide_scored_action.triggered.connect(self.toggle_hide_scored_images)
        # self.treat_categories_as_scoring_action.triggered.connect(self.toggle_treat_categories_as_scoring)
        # self.auto_scroll_on_scoring_action.triggered.connect(self.toggle_auto_scroll_on_scoring)
        # self.write_to_filesystem_action.triggered.connect(self.toggle_write_to_filesystem)
        # self.export_action.triggered.connect(self.open_export_window)
        # self.settings_action.triggered.connect(self.open_settings_window)
        # self.project_new_action.triggered.connect(self.new_project)
        # self.project_migrate_action.triggered.connect(self.migrate_project)

    def setup_mode_switching(self):
        # Add mode switch in menu bar
        view_menu = self.menuBar().addMenu('View')
        mode_menu = view_menu.addMenu('Mode')
        
        scoring_action = mode_menu.addAction('Scoring')
        tagging_action = mode_menu.addAction('Tagging')
        
        scoring_action.triggered.connect(lambda: self.switch_mode(0))
        tagging_action.triggered.connect(lambda: self.switch_mode(1))

    def setup_stacked_widget(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize modes
        self.scoring_mode = ScoringPage(self)
        # self.tagging_mode = TaggingMode(self)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(self.scoring_mode)
        # self.stacked_widget.addWidget(self.tagging_mode)

        self.stackedLayout.addWidget(self.stacked_widget)

    def switch_mode(self, index):
        self.stacked_widget.setCurrentIndex(index)

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    set_dark_mode(app)
    ex = DatasetClassifier()
    ex.show()
    sys.exit(app.exec())