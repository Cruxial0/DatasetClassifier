from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMessageBox
from src.styling.style_manager import StyleManager

EMOJI_FONT_FAMILIES = [
    "Segoe UI",           # Windows base font
    "Segoe UI Emoji",     # Windows emoji
    "Apple Color Emoji",  # macOS emoji
    "Noto Color Emoji",   # Linux emoji
    "sans-serif"          # Generic fallback
]

EMOJI_STYLE = 'font-family: "Segoe UI", "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif;'

def create_emoji_font(base_size=None):
    font = QFont()
    font.setFamilies(EMOJI_FONT_FAMILIES)
    if base_size:
        font.setPointSize(base_size)
    return font

def inline_emoji(emoji: str) -> str:
    return f'<span style="{EMOJI_STYLE}">{emoji}</span>'

def styled_information_box(parent, title: str, text: str, style_manager: StyleManager):
    message_box = QMessageBox(parent)
    message_box.setStyleSheet(style_manager.get_stylesheet(QMessageBox))
    message_box.setIcon(QMessageBox.Icon.Information)
    message_box.setWindowTitle(title)
    message_box.setText(text)
    message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    return message_box.exec()

def styled_warning_box(parent, title: str, text: str, style_manager: StyleManager):
    message_box = QMessageBox(parent)
    message_box.setStyleSheet(style_manager.get_stylesheet(QMessageBox))
    message_box.setIcon(QMessageBox.Icon.Warning)
    message_box.setWindowTitle(title)
    message_box.setText(text)
    message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    return message_box.exec()

def styled_question_box(parent, title: str, text: str, style_manager: StyleManager,
                       buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                       default_button=QMessageBox.StandardButton.No):
    message_box = QMessageBox(parent)
    message_box.setStyleSheet(style_manager.get_stylesheet(QMessageBox))
    message_box.setIcon(QMessageBox.Icon.Question)
    message_box.setWindowTitle(title)
    message_box.setText(text)
    message_box.setStandardButtons(buttons)
    message_box.setDefaultButton(default_button)
    return message_box.exec()
