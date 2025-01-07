from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget)

# Parent Dependencies
from src.database.database import Database
from src.project import Project
from src.config_handler import ConfigHandler
from src.update_poller import UpdatePoller
from src.styling.style_manager import StyleManager

# Settings Pages
from src.windows.settings_pages.tag_groups_settings import TagGroupSettings
from src.windows.settings_pages.behaviour_settings import BehaviourSettings
from src.windows.settings_pages.colors_settings import ColorsSettingsPage
from src.windows.settings_pages.export_settings import ExportSettingsPage
from src.windows.settings_pages.keybind_settings import KeybindSettingsPage
from src.windows.settings_pages.scoring_settings import ScoringSettingsPage
from src.windows.settings_pages.privacy_settings import PrivacySettingsPage

class SettingsWindow(QMainWindow):
    def __init__(self, parent, path: str = None):
        super().__init__()
        
        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 600)
        
        self.db: Database = parent.db
        self.active_project: Project = parent.active_project
        self.update_poller: UpdatePoller = parent.update_poller
        self.config_handler: ConfigHandler = parent.config_handler
        self.style_manager: StyleManager = parent.style_manager
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create navigation bar
        nav_widget = QWidget()
        nav_widget.setFixedWidth(200)
        nav_layout = QVBoxLayout(nav_widget)
        
        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        
        # Initialize pages dict but don't create pages yet
        self._pages = {}
        self._page_creators = {
            "behaviour": lambda: BehaviourSettings(self),
            "export": lambda: ExportSettingsPage(self),
            "keybinds": lambda: KeybindSettingsPage(self),
            "colors": lambda: ColorsSettingsPage(self),
            "scoring": lambda: ScoringSettingsPage(self),
            "privacy": lambda: PrivacySettingsPage(self),
            "tag_groups": lambda: TagGroupSettings(self)
        }
        
        # Add navigation buttons
        for name in self._page_creators.keys():
            btn = QPushButton(name.replace('_', ' ').title())
            btn.setCheckable(True)
            btn.setStyleSheet(self.style_manager.get_stylesheet(QPushButton, 'menu_tab'))
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        # Add widgets to main layout
        layout.addWidget(nav_widget)
        layout.addWidget(self.content_stack)
        
        if path:
            self.navigate_path(path)
            return

        # Select first page by default
        first_button = nav_widget.findChild(QPushButton)
        if first_button:
            first_button.setChecked(True)
            self.switch_page(list(self._page_creators.keys())[0])

    def navigate_path(self, path: str = None):
        """Navigate to a path in the settings window based on dot notation"""
        if path is None:
            return
        
        if '.' not in path:
            self.switch_page(path)
            return
        
        page = path.split('.')[0]

        self.switch_page(page)
        if page in ['tag_groups']:
            self._pages[page].navigate_path(".".join(path.split('.')[1:]))

    def get_page(self, page_name: str):
        """Get or create a page"""
        if page_name not in self._pages:
            creator = self._page_creators.get(page_name)
            if creator:
                self._pages[page_name] = creator()
                self.content_stack.addWidget(self._pages[page_name])
        return self._pages.get(page_name)

    def switch_page(self, page_name: str):
        # convert page_name to snake_case
        page_name = page_name.replace(' ', '_').lower()
        
        # Uncheck all buttons except the clicked one
        nav_buttons = self.findChildren(QPushButton)
        for button in nav_buttons:
            if button.text().replace(' ', '_').lower() == page_name:
                button.setChecked(True)
            else:
                button.setChecked(False)
        
        # Get or create the page and switch to it
        page = self.get_page(page_name)
        if page:
            self.content_stack.setCurrentWidget(page)