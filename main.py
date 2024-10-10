import os
import sys
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QMainWindow, QApplication, QWidget, QLabel)
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
from PyQt6.QtCore import Qt, QTimer, QSize
from src.button_states import ButtonStateManager
from src.database import Database
from src.config_handler import ConfigHandler
from src.ui_components import UIComponents
from src.image_handler import ImageHandler
from src.utils import key_to_unicode

class ImageScorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.default_scores = ['score_9', 'score_8_up', 'score_7_up', 'score_6_up', 'score_5_up', 'score_4_up', 'discard']
        self.db = Database()
        self.config_handler = ConfigHandler()
        self.button_states = ButtonStateManager()
        self.score_layout = None
        self.treat_categories_as_scoring = self.config_handler.get_treat_categories_as_scoring()
        self.image_handler = ImageHandler(self.db, self.config_handler)
        self.custom_shortcuts = {}
        self.category_buttons = []
        self.hide_scored_images = False
        self.alt_pressed = False
        self.ctrl_pressed = False
        self.initUI()
        self.load_config()

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
        options_menu = menu_bar.addMenu('Options')

        actions = UIComponents.create_menu_actions(self.config_handler)
        self.hide_scored_action, self.use_copy_category_action, self.use_copy_default_action, \
        self.treat_categories_as_scoring_action, self.auto_scroll_on_scoring_action = actions

        view_menu.addAction(self.hide_scored_action)
        # options_menu.addAction(self.use_copy_category_action)
        # options_menu.addAction(self.use_copy_default_action)
        # options_menu.addAction(self.treat_categories_as_scoring_action)
        options_menu.addAction(self.auto_scroll_on_scoring_action)

        self.hide_scored_action.triggered.connect(self.toggle_hide_scored_images)
        self.use_copy_category_action.triggered.connect(self.toggle_use_copy_category)
        self.use_copy_default_action.triggered.connect(self.toggle_use_copy_default)
        self.treat_categories_as_scoring_action.triggered.connect(self.toggle_treat_categories_as_scoring)
        self.auto_scroll_on_scoring_action.triggered.connect(self.toggle_auto_scroll_on_scoring)

    def create_directory_selection(self):
        layout, self.input_path, self.output_path, input_button, output_button = UIComponents.create_directory_selection(self.button_states.input_enabled)
        self.button_states.declare_button_group([self.output_path, output_button], 'input')
        input_button.clicked.connect(lambda: self.select_directory('input'))
        output_button.clicked.connect(lambda: self.select_directory('output'))
        return layout

    def create_middle_row(self):
        layout = QHBoxLayout()
        
        image_viewer_layout, self.prev_button, self.image_label, self.next_button = UIComponents.create_image_viewer(self.button_states.image_enabled)
        layout.addLayout(image_viewer_layout, 7)

        self.prev_button.clicked.connect(self.load_previous_image)
        self.next_button.clicked.connect(self.load_next_image)

        category_buttons_layout, self.category_input, self.category_add_button, self.category_button_layout = UIComponents.create_category_buttons(self.button_states.category_enabled)
        layout.addLayout(category_buttons_layout, 3)

        self.category_input.textChanged.connect(self.check_category_button_name)
        self.category_add_button.clicked.connect(self.add_category_button)

        self.button_states.declare_button_group([self.prev_button, self.next_button], 'image')
        self.button_states.declare_button_group([self.category_input, self.category_add_button], 'category')

        return layout

    def create_scoring_buttons(self):
        layout, self.score_buttons, self.progress_bar, self.progress_label = UIComponents.create_scoring_buttons(self.default_scores, self.button_states.score_enabled)
        self.button_states.declare_button_group(self.score_buttons, 'score')
        self.score_layout = layout.itemAt(0).layout()  # Store the score_layout
        for button in self.score_buttons:
            button.clicked.connect(lambda checked, s=button.text(): self.on_score_button_click(s, button))
        return layout

    def on_score_button_click(self, score, button):
        accent_color = self.config_handler.get_color('accent_color')
        button.setStyleSheet(f"background-color: {accent_color};")
        QTimer.singleShot(150, lambda: self.score_image(score))

    def toggle_hide_scored_images(self):
        self.hide_scored_images = self.hide_scored_action.isChecked()
        self.load_images()

    def select_directory(self, dir_type):
        folder = QFileDialog.getExistingDirectory(self, f"Select {dir_type.capitalize()} Directory")
        if folder:
            if dir_type == 'input':
                self.input_path.setText(folder)
                self.button_states.toggle_button_group(True, 'input')
                self.button_states.toggle_button_group(True, 'image')
                self.load_images()
                
            else:
                self.output_path.setText(folder)
                self.image_handler.set_output_folder(folder)
                self.rebuild_database(self.input_path.text(), folder)
                self.check_for_custom_scorings(folder)
                self.button_states.toggle_button_group(True, 'category')
                self.button_states.toggle_button_group(True, 'score')
                self.update_button_colors()

    def rebuild_database(self, input_folder, output_folder):
        if self.db.rebuild_from_sidecar():
            QMessageBox.information(self, "Database Rebuilt", "Database has been rebuilt from the sidecar file.")
        else:
            self.db.rebuild_from_filesystem(input_folder, output_folder)
            QMessageBox.information(self, "Database Rebuilt", "Database has been rebuilt from the filesystem.")
        self.db.write_sidecar()

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
            
            keybind_label = QLabel()
            keybind_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            keybind_label.setFixedWidth(30)  # Set a fixed width of 30px
            keybind_label.setStyleSheet("min-width: 30px; max-width: 30px;")  # Ensure the width is exactly 30px
            
            button_layout = QHBoxLayout()
            button_layout.addWidget(keybind_label)
            button_layout.addWidget(button)
            button_layout.addWidget(remove_button)
            
            self.category_button_layout.addLayout(button_layout)
            self.category_buttons.append((button, remove_button, keybind_label))
            self.apply_keybindings()

    def load_images(self):
        self.image_handler.load_images(self.input_path.text(), self.hide_scored_images)
        self.update_progress()
        self.display_image()

    def display_image(self):
        pixmap = self.image_handler.get_current_image()
        if pixmap:
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
            self.update_progress()
            self.update_button_colors()
            QTimer.singleShot(100, self.image_handler.preload_images)

    def update_progress(self):
        current, total = self.image_handler.get_progress()
        if total > 0:
            self.progress_bar.setValue(current * 100 // total)
            self.progress_label.setText(f"{current}/{total}")


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Alt:
            self.alt_pressed = True
            self.update_button_colors()
        elif event.key() == Qt.Key.Key_Control:
            self.ctrl_pressed = True
            self.update_button_colors()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Alt:
            self.alt_pressed = False
            self.update_button_colors()
        elif event.key() == Qt.Key.Key_Control:
            self.ctrl_pressed = False
            self.update_button_colors()
        else:
            super().keyReleaseEvent(event)

    def update_button_colors(self):
        current_image = self.image_handler.get_current_image_path()
        if not current_image:
            return
        
        current_score, current_categories = self.db.get_image_score(current_image)
        accent_color = self.config_handler.get_color('accent_color')
        alternate_color = self.config_handler.get_color('alternate_color')
        warning_color = self.config_handler.get_color('warning_color')
        select_color = self.config_handler.get_color('select_color')
        
        # Update default score buttons
        for i in range(self.score_layout.count()):
            button = self.score_layout.itemAt(i).widget()
            if isinstance(button, QPushButton):
                if not button.isEnabled(): continue
                if button.objectName() == current_score:
                    if button.objectName() == 'discard':
                        button.setStyleSheet(f"background-color: {warning_color}; color: white;")
                    else:
                        button.setStyleSheet(f"background-color: {accent_color}; color: white;")
                else:
                    if button.objectName() == 'discard':
                        button.setStyleSheet(f"background-color: {alternate_color}; color: white;")
                    else:
                        button.setStyleSheet("")
        
        # Update category buttons
        for button, remove_button, _ in self.category_buttons:
            if not button.isEnabled(): continue
            is_active = button.text() in current_categories
            
            if is_active:
                button.setStyleSheet(f"background-color: {alternate_color}; color: white;")
            else:
                button.setStyleSheet("")
            
            if self.alt_pressed and not self.ctrl_pressed:
                if not is_active:
                    button.setStyleSheet(f"background-color: {select_color}; color: white;")
                else:
                    button.setStyleSheet(f"background-color: {warning_color}; color: white;")
            elif self.ctrl_pressed:
                remove_button.setStyleSheet(f"background-color: {warning_color}; color: white;")
            else:
                remove_button.setStyleSheet("")

    def score_image(self, score):
        current_image_path = self.image_handler.get_current_image_path()
        if current_image_path:
            current_score, _ = self.db.get_image_score(current_image_path)
            
            if score in self.default_scores:
                new_score = score
                new_categories = []
            else:
                new_score = current_score
                new_categories = [score]

            if self.image_handler.score_image(new_score, new_categories):
                self.update_button_colors()
                if score in self.default_scores and self.config_handler.get_auto_scroll_on_scoring():
                    self.load_next_image()

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

    def load_next_image(self):
        if self.image_handler.load_next_image():
            self.display_image()

    def load_previous_image(self):
        if self.image_handler.load_previous_image():
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
                    unicode = key_to_unicode(key)
                    if not f"({unicode})" in button.text():
                        button.setText(f"({unicode})        {button.text()}")
                    button.setToolTip(f"Shortcut: {key}")
            elif action.startswith('custom_'):
                index = int(action.split('_')[1]) - 1
                if index < len(self.category_buttons):
                    button, _, keybind_label = self.category_buttons[index]
                    shortcut = QShortcut(QKeySequence(f"ALT+{key}"), self)
                    shortcut.activated.connect(lambda checked=False, b=button: self.score_image(b.text()))
                    self.custom_shortcuts[action] = shortcut
                    button.setToolTip(f"Shortcut: ALT+{key}")
                    keybind_label.setText(f"{key}")

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

    def add_category_button(self):
        if len(self.category_buttons) < 10:
            name = self.category_input.text()
            if name and not any(button[0].text() == name for button in self.category_buttons):
                button = QPushButton(name)
                button.clicked.connect(lambda _, s=name: self.score_image(s))
                remove_button = QPushButton("-")
                remove_button.setMaximumWidth(30)
                remove_button.clicked.connect(lambda _, b=button: self.remove_category_button(b))
                
                keybind_label = QLabel()
                keybind_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                keybind_label.setFixedWidth(40)  # Set a fixed width of 30px
                keybind_label.setStyleSheet("min-width: 40px; max-width: 40px;")  # Ensure the width is exactly 30px
                
                button_layout = QHBoxLayout()
                button_layout.addWidget(keybind_label)
                button_layout.addWidget(button)
                button_layout.addWidget(remove_button)
                
                self.category_button_layout.addLayout(button_layout)
                self.category_buttons.append((button, remove_button, keybind_label))
                self.category_input.clear()
                self.apply_keybindings()

    def remove_category_button(self, button):
        for i, (category_button, remove_button, keybind_label) in enumerate(self.category_buttons):
            if category_button == button:
                self.category_button_layout.itemAt(i).layout().itemAt(0).widget().deleteLater()
                self.category_button_layout.itemAt(i).layout().itemAt(1).widget().deleteLater()
                self.category_button_layout.itemAt(i).layout().itemAt(2).widget().deleteLater()
                self.category_button_layout.itemAt(i).layout().deleteLater()
                self.category_buttons.pop(i)
                break
        self.apply_keybindings()

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
        # Loop through all scorings

    def toggle_auto_scroll_on_scoring(self):
        self.auto_scroll_on_scoring = self.auto_scroll_on_scoring_action.isChecked()
        self.config_handler.set_auto_scroll_on_scoring(self.auto_scroll_on_scoring)
        self.config_handler.save_config()

    def check_category_button_name(self):
        name = self.category_input.text()
        if name and any(button[0].text() == name for button in self.category_buttons):
            self.category_add_button.setStyleSheet(f"background-color: {self.config_handler.get_color('warning_color')}; color: white;")
        else:
            self.category_add_button.setStyleSheet(f"background-color: {self.config_handler.get_color('accent_color')}; color: white;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageScorer()
    ex.show()
    sys.exit(app.exec())
