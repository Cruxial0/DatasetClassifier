from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, 
                             QScrollArea, QSizePolicy, QProgressBar, QMessageBox)
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut, QAction
from PyQt6.QtCore import Qt, QTimer

from src.config_handler import ConfigHandler

class UIComponents:
    @staticmethod
    def create_directory_selection(state: bool):
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        input_path = QLineEdit()
        input_button = QPushButton('Select Input Directory')
        input_layout.addWidget(input_path)
        input_layout.addWidget(input_button)
        layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        output_path = QLineEdit(enabled=state)
        output_button = QPushButton('Select Output Directory', enabled=state)
        output_layout.addWidget(output_path)
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)

        return layout, input_path, output_path, input_button, output_button

    @staticmethod
    def create_image_viewer(state: bool):
        layout = QHBoxLayout()
        
        prev_button = QPushButton('<', enabled=state)
        layout.addWidget(prev_button)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_area = QScrollArea()
        scroll_area.setWidget(image_label)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        next_button = QPushButton('>', enabled=state)
        layout.addWidget(next_button)

        return layout, prev_button, image_label, next_button

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
    def create_scoring_buttons(default_scores, state: bool):
        layout = QVBoxLayout()

        score_layout = QHBoxLayout()
        score_buttons = []
        for score in default_scores:
            button = QPushButton(score, enabled=state)
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
        use_copy_category_action = QAction('Use copy for categories', checkable=True)
        use_copy_default_action = QAction('Use copy for scorings', checkable=True)
        treat_categories_as_scoring_action = QAction('Treat categories as scorings', checkable=True)
        auto_scroll_on_scoring_action = QAction('Auto-scroll on scoring', checkable=True, checked=config.get_option('auto_scroll_on_scoring'))
        auto_scroll_on_scoring_action.setToolTip('Automatically moves to the next image when a score button is clicked')
        write_to_filesystem = QAction('Write changes to file system', checkable=True, checked=config.get_option('write_to_filesystem'))
        write_to_filesystem.setToolTip('If true, instantly reflects any changes in the output directory by copying and moving images around.\nUses 100-1000+ times more storage space.')
        export = QAction('Export')

        return (hide_scored_action, treat_categories_as_scoring_action, 
                auto_scroll_on_scoring_action, export, write_to_filesystem)
