from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, 
                             QScrollArea, QSizePolicy, QProgressBar, QMessageBox)
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut, QAction
from PyQt6.QtCore import Qt, QTimer

class UIComponents:
    @staticmethod
    def create_directory_selection():
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        input_path = QLineEdit()
        input_button = QPushButton('Select Input Directory')
        input_layout.addWidget(input_path)
        input_layout.addWidget(input_button)
        layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        output_path = QLineEdit()
        output_button = QPushButton('Select Output Directory')
        output_layout.addWidget(output_path)
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)

        return layout, input_path, output_path, input_button, output_button

    @staticmethod
    def create_image_viewer():
        layout = QHBoxLayout()
        
        prev_button = QPushButton('<')
        layout.addWidget(prev_button)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_area = QScrollArea()
        scroll_area.setWidget(image_label)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        next_button = QPushButton('>')
        layout.addWidget(next_button)

        return layout, prev_button, image_label, next_button

    @staticmethod
    def create_category_buttons():
        layout = QVBoxLayout()
        category_input = QLineEdit()
        category_input.setPlaceholderText('Add category')
        category_add_button = QPushButton('Add')
        category_add_button.setObjectName('category_add_button')
        layout.addWidget(category_input)
        layout.addWidget(category_add_button)
        category_button_layout = QVBoxLayout()
        layout.addLayout(category_button_layout)
        layout.addStretch(1)
        return layout, category_input, category_add_button, category_button_layout

    @staticmethod
    def create_scoring_buttons(default_scores):
        layout = QVBoxLayout()

        score_layout = QHBoxLayout()
        score_buttons = []
        for score in default_scores:
            button = QPushButton(score)
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
    def create_menu_actions():
        hide_scored_action = QAction('Hide Scored Images', checkable=True)
        use_copy_category_action = QAction('Use copy for categories', checkable=True)
        use_copy_default_action = QAction('Use copy for scorings', checkable=True)
        treat_categories_as_scoring_action = QAction('Treat categories as scorings', checkable=True)
        auto_scroll_on_scoring_action = QAction('Auto-scroll on scoring', checkable=True)

        return (hide_scored_action, use_copy_category_action, use_copy_default_action,
                treat_categories_as_scoring_action, auto_scroll_on_scoring_action)
