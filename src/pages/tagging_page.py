from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QSizePolicy, QProgressBar
from PyQt6.QtCore import Qt

from src.button_states import ButtonStateManager
from src.config_handler import ConfigHandler
from src.database.database import Database
from src.update_poller import UpdatePoller

class TaggingPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.button_states: ButtonStateManager = parent.button_states
        self.db: Database = parent.db
        self.update_poller: UpdatePoller = parent.update_poller
        self.config_handler: ConfigHandler = parent.config_handler
        self.active_project = parent.active_project

        self.setupUI()

        self.update_poller.add_method('update_tag_groups', self.update_tag_groups)

    def setupUI(self):
        self.main_layout = QHBoxLayout(self)
        self._create_image_viewer()
        self._create_tagging_interface()
        
    def _create_image_viewer(self):
        image_viewer_layout = QVBoxLayout()
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        scroll_area = QScrollArea()
        scroll_area.setWidget(image_label)
        scroll_area.setWidgetResizable(True)

        image_viewer_layout.addWidget(image_label)

        self.main_layout.addLayout(image_viewer_layout, 7)

    def show_configure_tag_groups(self):
        self.parent.open_settings_window('tag_groups')

    def update_tag_groups(self):
        self.tag_groups = self.db.tags.get_project_tags(self.active_project.id)

        if self.tag_groups is None: 
            return
        
        # Update label to tag group name
        self.tag_group_label.setText(self.tag_groups[0].name)

        # Create buttons for each tag in the first group
        self.active_tags = self.tag_groups[0].tags
        
        # Remove all items in the tags layout
        while self.tags_layout.count() > 0:
            self.tags_layout.takeAt(0).widget().deleteLater()
        
        for tag in self.active_tags:
            btn = QPushButton(tag.name)
            btn.setText(tag.name)
            self.tags_layout.addWidget(btn)

    def _create_tagging_interface(self):
        tagging_layout = QVBoxLayout()

        # Headers
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(7, 0, 7, 0)
        self.tag_group_label = QLabel("TAG_GROUP")
        self.tag_group_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.score_label = QLabel("SCORE")
        self.tag_group_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.score_label = QLabel("SCORE")
        self.score_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.config_handler.get_color('accent_color')};
                color: white;
                padding: 5px 10px;
                border-radius: 8px;
                font-weight: bold;
            }}
        """)

        header_layout.addWidget(self.tag_group_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.score_label)

        # Tags
        self.tags_layout = QVBoxLayout()
        self.tags_layout.setContentsMargins(7, 7, 7, 7)

        tag_groups = self.db.tags.get_project_tags(self.active_project.id)
        if tag_groups is not None and len(tag_groups) > 0:
            self.update_tag_groups()
        else:
            add_button = QPushButton("Configure Tag Groups")
            add_button.setStyleSheet(f"background-color: {self.config_handler.get_color('accent_color')}; color: white;")
            add_button.clicked.connect(self.show_configure_tag_groups)
            self.tags_layout.addWidget(add_button)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(7, 7, 7, 7)

        continue_btn = QPushButton("Continue")
        skip_btn = QPushButton("Skip")
        controls_layout.addWidget(continue_btn)
        controls_layout.addWidget(skip_btn)
        
        # Progress bar
        progress_layout = QHBoxLayout()

        progress_bar = QProgressBar()
        progress_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        progress_label = QLabel("0/0")
        progress_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        progress_layout.addWidget(progress_bar)
        progress_layout.addWidget(progress_label)

        # Ordering
        tagging_layout.addLayout(header_layout)
        tagging_layout.addLayout(self.tags_layout)
        tagging_layout.addStretch(1)
        tagging_layout.addLayout(controls_layout)
        tagging_layout.addLayout(progress_layout)

        self.main_layout.addLayout(tagging_layout, 3)