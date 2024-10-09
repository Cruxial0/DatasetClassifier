import os

def get_image_files(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

def create_directory(path):
    os.makedirs(path, exist_ok=True)
