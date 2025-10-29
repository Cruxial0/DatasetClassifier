from PyQt6.QtGui import QFont, QFontDatabase

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