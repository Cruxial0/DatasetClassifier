from PyQt6.QtWidgets import (QHBoxLayout, QMainWindow, QWidget, QStackedWidget, QMessageBox, QMenu, QMenuBar, QPushButton)
from PyQt6.QtCore import Qt
from src.export import Exporter
from src.pages.tagging_page import TaggingPage
from src.pages.scoring_page import ScoringPage
from src.database.database import Database
from src.project import Project
from src.button_states import ButtonStateManager
from src.config_handler import ConfigHandler
from src.ui_components import UIComponents
from src.popups.export_popup import ExportPopup
from src.windows.settings_window import SettingsWindow
from src.update_poller import UpdatePoller
from src.utils import open_directory
from src.styling.style_manager import StyleManager
from src.styling.styling_utils import styled_question_box, styled_information_box

# dataset_classifier.py
class DatasetClassifier(QMainWindow):
    def __init__(self, database: Database, project: Project):
        super().__init__()
        self.active_project = project
        self.db = database
        self.config_handler = ConfigHandler()
        self.button_states = ButtonStateManager()
        self.update_poller = UpdatePoller()
        self.style_manager = StyleManager(self.config_handler)

        self.settings_window = None
        
        self.setStyleSheet(self.style_manager.get_stylesheet(QMainWindow))

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
        menu_bar.setStyleSheet(self.style_manager.get_stylesheet(QMenuBar))

        file_menu = menu_bar.addMenu('File')
        view_menu = menu_bar.addMenu('View')

        file_menu.setToolTipsVisible(True)
        file_menu.setStyleSheet(self.style_manager.get_stylesheet(QMenu))
        view_menu.setToolTipsVisible(True)
        view_menu.setStyleSheet(self.style_manager.get_stylesheet(QMenu))

        actions = UIComponents.create_menu_actions(self.config_handler)
        self.hide_scored_action, self.export_action, self.settings_action, self.menu_button = actions  

        button_widget = QWidget()
        button_widget.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'accent'))
        layout = QHBoxLayout(button_widget)
        layout.addStretch()  # This pushes the button to the right
        layout.addWidget(self.menu_button)
        layout.setContentsMargins(0, 0, 0, 0)  
        menu_bar.setCornerWidget(button_widget)

        file_menu.addAction(self.export_action)
        file_menu.addAction(self.settings_action)
        view_menu.addAction(self.hide_scored_action)
        self.menu_button.clicked.connect(self.switch_mode)

        # self.hide_scored_action.triggered.connect(self.toggle_hide_scored_images)
        self.export_action.triggered.connect(self.open_export_window)
        self.settings_action.triggered.connect(lambda: self.open_settings_window())

    def switch_mode(self):
        self.current_mode = 1 if self.current_mode == 0 else 0

        if self.current_mode == 0:
            self.scoring_page.set_active()
            self.tagging_page.set_active(False)
        else:
            self.tagging_page.set_active()
            self.scoring_page.set_active(False)

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

    def open_settings_window(self, path: str = None):
        if self.settings_window is not None:
            self.settings_window.setWindowState(self.settings_window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
            self.settings_window.setFocus(Qt.FocusReason.PopupFocusReason)
            self.settings_window.activateWindow()

            self.settings_window.navigate_path(path)
            return

        self.settings_window = SettingsWindow(self, path)
    
        def handle_close(event):
            self.settings_window = None
            event.accept()
        
        self.settings_window.closeEvent = handle_close
        self.settings_window.show()

    def open_export_window(self):
        self.export_popup = ExportPopup(
            export_callback=self.export_callback,
            categories=self.db.images.get_unique_categories(self.active_project.id),
            project_id=self.active_project.id,
            config=self.config_handler,
            style_manager= self.style_manager
        )
        self.export_popup.show()

    # Callbacks

    def export_callback(self, data):
        # Check if there is anything to export
        if not self.db.projects.has_scores(self.active_project.id) and not self.db.projects.has_tags(self.active_project.id):
            styled_information_box(self, "Export", "There are no images to export.", self.style_manager)
            return
        
        exporter = Exporter(data, self.db, self.config_handler)
        
        export_items = exporter.process_export(self.db.images.get_export_images(self.active_project.id)).items()

        if len(export_items) == 0:
            styled_information_box(self, "Export", "No images found matching the export criteria.", self.style_manager)
            return

        # Display summary
        summary = f"Export path: {exporter.output_dir}"
        for key, value in export_items:
            summary += f"\n - {value} images exported to '{key}'"

        confirm = styled_question_box(self, 'Export summary', 
            f"{summary}\n\nConfirm?",
            self.style_manager,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            dir_confirm = styled_question_box(self, 'Confirm deleting directory', 
                'All files in the output directory will be deleted.\n\nConfirm?',
                self.style_manager,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No)
            if dir_confirm == QMessageBox.StandardButton.Yes:
                exporter.export()
                styled_information_box(self, "Workspace", "The workspace has been exported.", self.style_manager)
                self.export_popup.close()
                open_directory(exporter.output_dir)