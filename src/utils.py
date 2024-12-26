import os
from datetime import datetime
from pathlib import Path
import pytz
from zoneinfo import ZoneInfo
from typing import Optional
from tzlocal import get_localzone

def get_image_files(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp'))]

def get_image_paths(directory):
    """
    Returns a list of image paths in the given directory (posix-formatted)
    """
    return [Path(directory, f).absolute().as_posix() for f in get_image_files(directory)]

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

def get_time_ago(timestamp_str: str, timezone: Optional[str] = None) -> str:
    """
    Convert a timestamp string to a human-readable relative time string.
    Uses system timezone by default, with optional timezone override.
    
    Args:
        timestamp_str: ISO format timestamp string
        timezone: Optional timezone name override (e.g. "America/New_York", "Asia/Tokyo")
        
    Returns:
        str: Human readable string like "2 hours ago"
    """
    # Parse the timestamp string to datetime object
    timestamp = datetime.fromisoformat(timestamp_str)
    
    # If timestamp has no timezone, assume UTC
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=ZoneInfo("UTC"))
    
    # Get system timezone if none specified
    if timezone is None:
        target_tz = get_localzone()
    else:
        try:
            target_tz = ZoneInfo(timezone)
        except KeyError:
            raise ValueError(f"Invalid timezone: {timezone}")
        
    now = datetime.now(target_tz)
    
    # Convert timestamp to target timezone for comparison
    timestamp = timestamp.astimezone(target_tz)
    
    # Calculate the time difference
    delta = now - timestamp
    seconds = delta.total_seconds()

    # Convert to appropriate time unit
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        unit = "minute" if minutes == 1 else "minutes"
        return f"{minutes} {unit} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        unit = "hour" if hours == 1 else "hours"
        return f"{hours} {unit} ago"
    elif seconds < 604800:  # 7 days
        days = int(seconds / 86400)
        unit = "day" if days == 1 else "days"
        return f"{days} {unit} ago"
    elif seconds < 2592000:  # 30 days
        weeks = int(seconds / 604800)
        unit = "week" if weeks == 1 else "weeks"
        return f"{weeks} {unit} ago"
    else:
        months = int(seconds / 2592000)
        unit = "month" if months == 1 else "months"
        return f"{months} {unit} ago"