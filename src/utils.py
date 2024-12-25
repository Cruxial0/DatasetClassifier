import os

def get_image_files(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp'))]

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def sanitize_string(string: str) -> str:
    """
    Sanitize a string to be used as a filename

    :param string: The string to sanitize
    :return: The sanitized string
    """
    illegal_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    replace_map = {
        ' ': '_',
    }

    # Strip all illegal characters
    string = ''.join(char for char in string if char not in illegal_chars)

    # Replace all values in replace_map
    for key, value in replace_map.items():
        string = string.replace(key, value)

    return string

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