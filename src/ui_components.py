from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, 
                             QScrollArea, QSizePolicy, QProgressBar, QMessageBox, QSpacerItem)
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut, QAction
from PyQt6.QtCore import Qt, QTimer

from src.config_handler import ConfigHandler

class UIComponents:
    @staticmethod
    def create_project_selection(state: bool):
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()

        input_path = QLineEdit()
        input_button = QPushButton('Load Project')

        input_layout.addWidget(input_path)
        input_layout.addWidget(input_button)
        
        layout.addLayout(input_layout)

        return layout, input_path, input_button

    @staticmethod
    def create_image_viewer(state: bool):
        layout = QHBoxLayout()
        
        container_left = QVBoxLayout()
        
        prev_button = QPushButton('<', enabled=state)
        prev_button.setObjectName("prev_button")
        to_latest_button_left = QPushButton('<<', enabled=state)
        to_latest_button_left.setObjectName("to_latest_button_left")

        container_left.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        container_left.addWidget(prev_button)
        container_left.addWidget(to_latest_button_left)
        container_left.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        layout.addLayout(container_left)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_area = QScrollArea()
        scroll_area.setWidget(image_label)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        container_right = QVBoxLayout()
        
        next_button = QPushButton('>', enabled=state)
        next_button.setObjectName("next_button")
        to_latest_button_right = QPushButton('>>', enabled=state)
        to_latest_button_right.setObjectName("to_latest_button_right")

        container_right.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        container_right.addWidget(next_button)
        container_right.addWidget(to_latest_button_right)
        container_right.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        layout.addLayout(container_right)

        return layout, prev_button, image_label, next_button, to_latest_button_right, to_latest_button_left

    @staticmethod
    def create_category_buttons(state: bool):
        layout = QVBoxLayout()
        category_input = QLineEdit(enabled=state)
        category_input.setPlaceholderText('Add category')
        category_add_button = QPushButton('Add', enabled=state)
        category_add_button.setObjectName('category_add_button')
        layout.addWidget(category_input)
        layout.addWidget(category_add_button)
        category_button_layout = QVBoxLayout()
        layout.addLayout(category_button_layout)
        layout.addStretch(1)
        return layout, category_input, category_add_button, category_button_layout

    @staticmethod
    def create_scoring_buttons(default_scores, state: bool, config: ConfigHandler):
        layout = QVBoxLayout()

        score_layout = QHBoxLayout()
        score_buttons = []
        for score in default_scores:
            if score == 'discard':
                button = QPushButton('discard', enabled=state)
            else:
                button = QPushButton(config.get_score(score), enabled=state)
                
            button.setObjectName(score)
            score_layout.addWidget(button)
            score_buttons.append(button)
        layout.addLayout(score_layout)

        progress_bar = QProgressBar()
        progress_label = QLabel('0/0')
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(progress_bar)
        progress_layout.addWidget(progress_label)
        layout.addLayout(progress_layout)

        return layout, score_buttons, progress_bar, progress_label

    @staticmethod
    def create_menu_actions(config: ConfigHandler):
        hide_scored_action = QAction('Hide Scored Images', checkable=True)
        hide_scored_action.setToolTip('Hides all images that are already scored')
        export = QAction('Export')
        settings = QAction('Settings')

        menu_button = QPushButton("Swtich Mode")
        menu_button.setFixedSize(100, 25)  # Adjust size as needed

        return (hide_scored_action, export, settings, menu_button)
