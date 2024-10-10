import os

def get_image_files(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def key_to_unicode(key: str) -> str:
    key_unicode_map = {
        "BACKSPACE": "⌫",
        "SHIFT": "⇧",
        "CTRL": "⌃",
        "ALT": "⎇",
        "ENTER": "⏎",
        "TAB": "⇥",
        "ESC": "⎋",
        "UP": "↑",
        "DOWN": "↓",
        "LEFT": "←",
        "RIGHT": "→",
        "CAPSLOCK": "⇪",
        "DELETE": "⌦",
        "HOME": "⇱",
        "END": "⇲",
        "PAGEUP": "⇞",
        "PAGEDOWN": "⇟",
        "INSERT": "⎀",
        "COMMAND": "⌘",  # MacOS Command key
        "OPTION": "⌥",   # MacOS Option key
    }

    return key_unicode_map.get(key.upper(), key)