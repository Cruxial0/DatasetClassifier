from asyncio import sleep
import sys
import os
import shutil
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QLineEdit, 
                             QScrollArea, QSizePolicy, QProgressBar, QMessageBox,
                             QMainWindow)
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut, QColor, QAction
from PyQt6.QtCore import Qt, QTimer
from src.database import Database
from src.utils import get_image_files, create_directory
from src.config_handler import ConfigHandler

class ImageScorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.default_scores = ['score_9', 'score_8_up', 'score_7_up', 'score_6_up', 'score_5_up', 'score_4_up', 'discard']
        self.db = Database()
        self.config_handler = ConfigHandler()
        self.custom_shortcuts = {}
        self.use_copy_category = self.config_handler.get_use_copy_category()
        self.use_copy_default = self.config_handler.get_use_copy_default()
        self.treat_categories_as_scoring = self.config_handler.get_treat_categories_as_scoring()
        self.auto_scroll_on_scoring = self.config_handler.get_auto_scroll_on_scoring()
        self.initUI()
        self.current_image = None
        self.input_folder = None
        self.output_folder = None
        self.category_buttons = []
        self.image_list = []
        self.current_index = -1
        self.preloaded_images = {}
        self.hide_scored_images = False
        self.load_config()
        # self.load_workspace()

    def initUI(self):
        self.setWindowTitle('Image Scorer')
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.create_menu_bar()
        main_layout.addLayout(self.create_directory_selection())
        main_layout.addLayout(self.create_middle_row())
        main_layout.addLayout(self.create_scoring_buttons())

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        view_menu = menu_bar.addMenu('View')
        self.hide_scored_action = QAction('Hide Scored Images', self, checkable=True)
        self.hide_scored_action.triggered.connect(self.toggle_hide_scored_images)
        view_menu.addAction(self.hide_scored_action)

        options_menu = menu_bar.addMenu('Options')
        self.use_copy_category_action = QAction('Use copy for categories', self, checkable=True)
        self.use_copy_category_action.setChecked(self.use_copy_category)
        self.use_copy_category_action.triggered.connect(self.toggle_use_copy_category)
        options_menu.addAction(self.use_copy_category_action)

        self.use_copy_default_action = QAction('Use copy for scorings', self, checkable=True)
        self.use_copy_default_action.setChecked(self.use_copy_default)
        self.use_copy_default_action.triggered.connect(self.toggle_use_copy_default)
        options_menu.addAction(self.use_copy_default_action)

        self.treat_categories_as_scoring_action = QAction('Treat categories as scorings', self, checkable=True)
        self.treat_categories_as_scoring_action.setChecked(self.treat_categories_as_scoring)
        self.treat_categories_as_scoring_action.triggered.connect(self.toggle_treat_categories_as_scoring)
        options_menu.addAction(self.treat_categories_as_scoring_action)

        self.auto_scroll_on_scoring_action = QAction('Auto-scroll on scoring', self, checkable=True)
        self.auto_scroll_on_scoring_action.setChecked(self.auto_scroll_on_scoring)
        self.auto_scroll_on_scoring_action.triggered.connect(self.toggle_auto_scroll_on_scoring)
        options_menu.addAction(self.auto_scroll_on_scoring_action)

    def toggle_use_copy_category(self):
        self.use_copy_category = self.use_copy_category_action.isChecked()
        self.config_handler.set_use_copy_category(self.use_copy_category)
        self.config_handler.save_config()

    def toggle_use_copy_default(self):
        self.use_copy_default = self.use_copy_default_action.isChecked()
        self.config_handler.set_use_copy_default(self.use_copy_default)
        self.config_handler.save_config()

    def toggle_treat_categories_as_scoring(self):
        self.treat_categories_as_scoring = self.treat_categories_as_scoring_action.isChecked()
        self.config_handler.set_treat_categories_as_scoring(self.treat_categories_as_scoring)
        self.config_handler.save_config()

    def toggle_auto_scroll_on_scoring(self):
        self.auto_scroll_on_scoring = self.auto_scroll_on_scoring_action.isChecked()
        self.config_handler.set_auto_scroll_on_scoring(self.auto_scroll_on_scoring)
        self.config_handler.save_config()

    def create_directory_selection(self):
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        input_button = QPushButton('Select Input Directory')
        input_button.clicked.connect(lambda: self.select_directory('input'))
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(input_button)
        layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        output_button = QPushButton('Select Output Directory')
        output_button.clicked.connect(lambda: self.select_directory('output'))
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)

        return layout

    def create_middle_row(self):
        layout = QHBoxLayout()
        
        image_viewer_layout = self.create_image_viewer()
        layout.addLayout(image_viewer_layout, 7)

        category_buttons_layout = self.create_category_buttons()
        layout.addLayout(category_buttons_layout, 3)

        return layout

    def create_image_viewer(self):
        layout = QHBoxLayout()
        
        self.prev_button = QPushButton('<')
        self.prev_button.clicked.connect(self.load_previous_image)
        layout.addWidget(self.prev_button)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.next_button = QPushButton('>')
        self.next_button.clicked.connect(self.load_next_image)
        layout.addWidget(self.next_button)

        return layout

    def create_category_buttons(self):
        layout = QVBoxLayout()
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText('Add category')
        self.category_input.textChanged.connect(self.check_category_button_name)
        self.category_add_button = QPushButton('Add')
        self.category_add_button.setObjectName('category_add_button')
        self.category_add_button.clicked.connect(self.add_category_button)
        layout.addWidget(self.category_input)
        layout.addWidget(self.category_add_button)
        self.category_button_layout = QVBoxLayout()
        layout.addLayout(self.category_button_layout)
        layout.addStretch(1)
        return layout

    def check_category_button_name(self):
        name = self.category_input.text()
        if name and any(button[0].text() == name for button in self.category_buttons):
            self.category_add_button.setStyleSheet(f"background-color: {self.config_handler.get_color('alternate_color')}; color: white;")
        else:
            self.category_add_button.setStyleSheet(f"background-color: {self.config_handler.get_color('accent_color')}; color: white;")

    def add_category_button(self):
        if len(self.category_buttons) < 10:
            name = self.category_input.text()
            if name and not any(button[0].text() == name for button in self.category_buttons):
                button = QPushButton(name)
                button.clicked.connect(lambda _, s=name: self.score_image(s))
                remove_button = QPushButton("-")
                remove_button.setMaximumWidth(30)
                remove_button.clicked.connect(lambda _, b=button: self.remove_category_button(b))
                
                button_layout = QHBoxLayout()
                button_layout.addWidget(button)
                button_layout.addWidget(remove_button)
                
                self.category_button_layout.addLayout(button_layout)
                self.category_buttons.append((button, remove_button))
                self.category_input.clear()
                self.apply_keybindings()

    def remove_category_button(self, button):
        for i, (category_button, remove_button) in enumerate(self.category_buttons):
            if category_button == button:
                self.category_button_layout.itemAt(i).layout().itemAt(0).widget().deleteLater()
                self.category_button_layout.itemAt(i).layout().itemAt(1).widget().deleteLater()
                self.category_button_layout.itemAt(i).layout().deleteLater()
                self.category_buttons.pop(i)
                break
        self.apply_keybindings()

    def create_scoring_buttons(self):
        layout = QVBoxLayout()

        self.score_layout = QHBoxLayout()
        score_buttons = self.default_scores
        for score in score_buttons:
            button = QPushButton(score)
            button.setObjectName(score)
            button.clicked.connect(lambda checked, s=score, b=button: self.on_score_button_click(s, b))
            self.score_layout.addWidget(button)
        layout.addLayout(self.score_layout)

        self.progress_bar = QProgressBar()
        self.progress_label = QLabel('0/0')
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)

        return layout

    def on_score_button_click(self, score, button):
        accent_color = self.config_handler.get_color('accent_color')
        sleep(0.15)
        button.setStyleSheet(f"background-color: {accent_color};")
        self.score_image(score)
        


    def toggle_hide_scored_images(self):
        self.hide_scored_images = self.hide_scored_action.isChecked()
        self.load_images()

    def select_directory(self, dir_type):
        folder = QFileDialog.getExistingDirectory(self, f"Select {dir_type.capitalize()} Directory")
        if folder:
            if dir_type == 'input':
                self.input_folder = folder
                self.input_path.setText(folder)
                self.load_images()
            else:
                self.output_folder = folder
                self.output_path.setText(folder)
                self.check_for_custom_scorings(folder)

    def check_for_custom_scorings(self, folder):
        custom_scorings = []
        if not self.treat_categories_as_scoring:
            for default_score in self.default_scores:
                default_score_folder = os.path.join(folder, default_score)
                if os.path.isdir(default_score_folder):
                    for item in os.listdir(default_score_folder):
                        if os.path.isdir(os.path.join(default_score_folder, item)) and item not in self.default_scores:
                            custom_scorings.append(item)
        else:
            for item in os.listdir(folder):
                if os.path.isdir(os.path.join(folder, item)) and item not in self.default_scores:
                    custom_scorings.append(item)
        
        custom_scorings = list(set(custom_scorings))  # Remove duplicates
        
        if custom_scorings:
            reply = QMessageBox.question(self, 'Custom Scorings Detected', 
                                         "Custom Scorings were detected. Do you want to import them?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                for scoring in custom_scorings:
                    self.add_category_button_from_import(scoring)

    def add_category_button_from_import(self, name):
        if len(self.category_buttons) < 10 and not any(button[0].text() == name for button in self.category_buttons):
            button = QPushButton(name)
            button.clicked.connect(lambda _, s=name: self.score_image(s))
            remove_button = QPushButton("-")
            remove_button.setMaximumWidth(30)
            remove_button.clicked.connect(lambda _, b=button: self.remove_category_button(b))
            
            button_layout = QHBoxLayout()
            button_layout.addWidget(button)
            button_layout.addWidget(remove_button)
            
            self.category_button_layout.addLayout(button_layout)
            self.category_buttons.append((button, remove_button))
            self.apply_keybindings()

    def load_images(self):
        if self.input_folder:
            self.image_list = get_image_files(self.input_folder)
            if self.hide_scored_images:
                self.image_list = [img for img in self.image_list if not self.db.is_image_scored(os.path.join(self.input_folder, img))]
            self.current_index = 0
            self.update_progress()
            self.preload_images()
            self.display_image()

    def preload_images(self):
        self.preloaded_images.clear()
        start = max(0, self.current_index - 3)
        end = min(len(self.image_list), self.current_index + 4)
        for i in range(start, end):
            if i not in self.preloaded_images:
                image_path = os.path.join(self.input_folder, self.image_list[i])
                self.preloaded_images[i] = QPixmap(image_path)

    def display_image(self):
        if self.current_index < len(self.image_list):
            self.current_image = os.path.join(self.input_folder, self.image_list[self.current_index])
            if self.current_index in self.preloaded_images:
                pixmap = self.preloaded_images[self.current_index]
            else:
                pixmap = QPixmap(self.current_image)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
            self.update_progress()
            self.update_button_colors()
            QTimer.singleShot(100, self.preload_images)

    def update_progress(self):
        if self.image_list:
            self.progress_bar.setValue((self.current_index + 1) * 100 // len(self.image_list))
            self.progress_label.setText(f"{self.current_index + 1}/{len(self.image_list)}")

    def update_button_colors(self):
        if not self.current_image:
            return

        current_scores = self.db.get_image_scores(self.current_image)
        accent_color = self.config_handler.get_color('accent_color')
        alternate_color = self.config_handler.get_color('alternate_color')
        warning_color = self.config_handler.get_color('warning_color')
        
        # Update default score buttons
        for i in range(self.score_layout.count()):
            button = self.score_layout.itemAt(i).widget()
            if isinstance(button, QPushButton):
                if button.text() in current_scores:
                    if button.text() == 'discard':
                        button.setStyleSheet(f"background-color: {warning_color}; color: white;")
                    else:
                        button.setStyleSheet(f"background-color: {accent_color}; color: white;")
                else:
                    if button.text() == 'discard':
                        button.setStyleSheet(f"background-color: {alternate_color}; color: white;")
                    else:
                        button.setStyleSheet("")

        # Update category buttons
        for button, _ in self.category_buttons:
            if button.text() in current_scores:
                button.setStyleSheet(f"background-color: {alternate_color}; color: white;")
            else:
                button.setStyleSheet(f"color: white;")

    def score_image(self, score):
        if self.current_image and self.output_folder:
            is_category = score not in self.default_scores
            current_scores = self.db.get_image_scores(self.current_image)
            
            if score in current_scores:
                # Remove the score if it's already applied
                self.db.remove_score(self.current_image, score)
                self.remove_image_file(score)
            else:
                # Add the new score
                if is_category:
                    self.handle_category_scoring(score, current_scores)
                else:
                    self.handle_default_scoring(score, current_scores)

            self.update_button_colors()

            # Auto-scroll to next image if it's a scoring button and auto-scroll is enabled
            if not is_category and self.auto_scroll_on_scoring:
                self.load_next_image()

    def handle_category_scoring(self, category, current_scores):
        if self.treat_categories_as_scoring:
            dest_folder = os.path.join(self.output_folder, category)
        else:
            default_score = next((score for score in current_scores if score in self.default_scores), self.default_scores[0])
            dest_folder = os.path.join(self.output_folder, default_score, category)

        self.copy_image_to_folder(dest_folder)
        self.db.add_score(self.current_image, os.path.join(dest_folder, os.path.basename(self.current_image)), category)

    def handle_default_scoring(self, score, current_scores):
        dest_folder = os.path.join(self.output_folder, score)
        self.copy_image_to_folder(dest_folder)
        self.db.add_score(self.current_image, os.path.join(dest_folder, os.path.basename(self.current_image)), score)

        # Transfer existing categories to the new default score folder
        for old_score in current_scores:
            if old_score in self.default_scores:
                self.remove_image_file(old_score)
                self.db.remove_score(self.current_image, old_score)
            else:  # It's a category
                if not self.treat_categories_as_scoring:
                    old_default_score = next((s for s in current_scores if s in self.default_scores), None)
                    if old_default_score:
                        old_category_folder = os.path.join(self.output_folder, old_default_score, old_score)
                        new_category_folder = os.path.join(dest_folder, old_score)
                        old_image_path = os.path.join(old_category_folder, os.path.basename(self.current_image))
                        new_image_path = os.path.join(new_category_folder, os.path.basename(self.current_image))
                        
                        if os.path.exists(old_image_path):
                            create_directory(new_category_folder)
                            shutil.move(old_image_path, new_image_path)
                        
                        self.db.update_score(self.current_image, old_score, new_image_path)

        # Update categories for the new default score
        self.update_categories_for_default_score(score)

    def update_categories_for_default_score(self, default_score):
        for button, _ in self.category_buttons:
            category = button.text()
            dest_folder = os.path.join(self.output_folder, default_score, category)
            create_directory(dest_folder)
            dest_file = os.path.join(dest_folder, os.path.basename(self.current_image))
            
            if not os.path.exists(dest_file):
                shutil.copy2(self.current_image, dest_file)
                self.db.add_score(self.current_image, dest_file, category)

    def copy_image_to_folder(self, dest_folder):
        create_directory(dest_folder)
        dest_file = os.path.join(dest_folder, os.path.basename(self.current_image))
        shutil.copy2(self.current_image, dest_file)

    def remove_image_file(self, score):
        if self.treat_categories_as_scoring or score in self.default_scores:
            dest_file = os.path.join(self.output_folder, score, os.path.basename(self.current_image))
        else:
            default_score = next((s for s in self.db.get_image_scores(self.current_image) if s in self.default_scores), self.default_scores[0])
            dest_file = os.path.join(self.output_folder, default_score, score, os.path.basename(self.current_image))
        
        if os.path.exists(dest_file):
            os.remove(dest_file)

    def load_next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.display_image()

    def load_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image()

    def load_config(self):
        self.apply_keybindings()
        self.apply_accent_color()


    def apply_keybindings(self):
        # Clear existing shortcuts
        for shortcut in self.findChildren(QShortcut):
            shortcut.setEnabled(False)
            shortcut.deleteLater()
        self.custom_shortcuts.clear()

        keybindings = self.config_handler.get_keybindings()
        
        for action, key in keybindings.items():
            if action == 'image_next':
                QShortcut(QKeySequence(key), self, activated=self.load_next_image)
            elif action == 'image_previous':
                QShortcut(QKeySequence(key), self, activated=self.load_previous_image)
            elif action in self.default_scores:
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(lambda checked=False, s=action: self.score_image(s))
                button = self.findChild(QPushButton, action)
                if button:
                    button.setToolTip(f"Shortcut: {key}")
            elif action.startswith('custom_'):
                index = int(action.split('_')[1]) - 1
                if index < len(self.category_buttons):
                    button, _ = self.category_buttons[index]
                    shortcut = QShortcut(QKeySequence(key), self)
                    shortcut.activated.connect(lambda checked=False, b=button: self.score_image(b.text()))
                    self.custom_shortcuts[action] = shortcut
                    button.setToolTip(f"Shortcut: {key}")

    def apply_accent_color(self):
        accent_color = self.config_handler.get_color('accent_color')
        
        self.category_add_button.setStyleSheet(f"background-color: {accent_color}; color: white;")
        
        # for score in self.default_scores:
        #     button = self.findChild(QPushButton, score)
        #     if button:
        #         button.setStyleSheet(f"background-color: {accent_color}; color: white;")
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {accent_color};
                width: 10px;
                margin: 1px;
            }}
        """)
        
        self.progress_label.setStyleSheet(f"color: {accent_color};")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageScorer()
    ex.show()
    sys.exit(app.exec())
