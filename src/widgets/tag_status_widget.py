from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal  # Add this import

from src.config_handler import ConfigHandler
from src.tagging.tag_group import TagGroup

button_style = """
    QPushButton {
        background-color: #454545;
        color: white;
        padding: 5px 10px;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: #555555;
    }
    QPushButton:pressed {
        background-color: #353535;
    }
    QPushButton:disabled {
        background-color: #353535;
        color: #545454;
    }
"""

class TagStatusWidget(QWidget):
    next_clicked: pyqtSignal = pyqtSignal()
    prev_clicked: pyqtSignal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.config_handler: ConfigHandler = self.parent.config_handler

        self.active_group: TagGroup = None
        self.is_valid = False

        self.initUI()

    def initUI(self):
        container = QFrame(self)
        container.setStyleSheet("background-color: #292929; border-radius: 8px;")
        container.setFrameShadow(QFrame.Shadow.Raised)

        self.main_layout = QVBoxLayout(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(container)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        top_row_layout = QHBoxLayout()
        top_row_layout.setContentsMargins(0, 0, 0, 20)
        tag_group_layout = QVBoxLayout()

        ## Stats Layout
        # Tag group
        tag_group_stats_layout = QHBoxLayout()
        self.tag_group_status_label = QLabel("🔴")
        self.tag_group_name_label = QLabel("GROUP_TITLE")
        self.tag_group_index_label = QLabel("(0/0)")

        self.tag_group_name_label.setStyleSheet("color: white; font-weight: bold;")

        tag_group_stats_layout.addWidget(self.tag_group_status_label)
        tag_group_stats_layout.addWidget(self.tag_group_name_label)
        tag_group_stats_layout.addWidget(self.tag_group_index_label)

        # Selected tags
        self.seleted_tags_label = QLabel("0/0 selected")

        # Score
        self.score_label = QLabel("score_0")
        self.score_label.setStyleSheet(f"""
                                  background-color: {self.config_handler.get_color('accent_color')}; 
                                  color: white; padding: 
                                  5px 10px; border-radius: 8px;
                                  """)


        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.setContentsMargins(0, 0, 0, 0)

        ## Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # Add tag button
        skip_button = QPushButton("Skip")
        options_button = QPushButton("⚙️")

        self.prev_button = QPushButton("<")
        self.next_button = QPushButton(">")

        self.prev_button.clicked.connect(self.prev_clicked)
        self.next_button.clicked.connect(self.next_clicked)

        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

        buttons_layout.addWidget(skip_button)
        buttons_layout.addWidget(options_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.prev_button)
        buttons_layout.addWidget(self.next_button)

        for button in [skip_button, options_button, self.prev_button, self.next_button]:
            button.setStyleSheet(button_style)
        
        bottom_row_layout.addLayout(buttons_layout)

        tag_group_layout.addLayout(tag_group_stats_layout)
        tag_group_layout.addWidget(self.seleted_tags_label)

        top_row_layout.addLayout(tag_group_layout)
        top_row_layout.addStretch(1)
        top_row_layout.addWidget(self.score_label)

        self.main_layout.addLayout(top_row_layout)
        self.main_layout.addLayout(bottom_row_layout)

        # Add click events
        # skip_button.clicked.connect(self.on_skip_click)
        options_button.clicked.connect(self.on_options_click)
        # prev_button.clicked.connect(self.parent.load_previous_image)
        # next_button.clicked.connect(self.parent.load_next_image)

    def set_tag_groups(self, tag_groups: list[TagGroup]):
        self.tag_groups = tag_groups

    def set_active_group(self, order: int):
        self.active_group = self.tag_groups[order]
        self.update_group_ui()

    def update_group_ui(self):
        self.tag_group_name_label.setText(self.active_group.name)
        self.tag_group_index_label.setText(f"({self.active_group.order + 1}/{len(self.tag_groups)})")
        
        if self.active_group.allow_multiple:
            self.seleted_tags_label.setText(f"0/{self.active_group.min_tags} selected")
        else:
            self.seleted_tags_label.setText(f"0/1 selected")

    def set_prev_button_enabled(self, enabled: bool):
        self.prev_button.setEnabled(enabled)

    def set_next_button_enabled(self, enabled: bool):
        self.next_button.setEnabled(enabled)

    def check_group_conditions(self, selected_tags: list[int]) -> bool:
        if self.active_group is None:
            return
        
        # check how many tags exist in current group
        count = 0
        for group_tags in self.active_group.tags:
            count += 1 if group_tags.id in selected_tags else 0
        
        condition = count >= self.active_group.min_tags
        self.seleted_tags_label.setText(f"{count}/{self.active_group.min_tags} selected")
        self.tag_group_status_label.setText("🟢" if condition else "🔴")

        self.is_valid = condition

        self._update_button_states()

        return condition
       
    def update_score(self, score: str):
        self.score_label.setText(score)

    def _update_button_states(self):
        self.next_button.setEnabled(self.is_valid)

    def on_options_click(self):
        self.parent.show_configure_tag_groups()