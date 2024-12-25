import os
from pathlib import Path
import shutil
from PyQt6.QtGui import QPixmap
from src.database.database import Database
from src.utils import create_directory
from PIL import Image
from PIL.ExifTags import TAGS

class ImageHandler:
    def __init__(self, db: Database, config_handler):
        self.db = db
        self.config_handler = config_handler
        self.input_folder = None
        self.output_folder = None
        self.image_list = []
        self.current_index = -1
        self.current_image = None
        self.preloaded_images = {}

    def set_db(self, db):
        self.db = db

    def load_images(self, input_folder, hide_scored_images):
        self.input_folder = input_folder
        print(input_folder)
        self.image_list = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if hide_scored_images:
            self.image_list = [img for img in self.image_list if not self.db.images.is_image_scored(os.path.join(self.input_folder, img))]
        self.current_index = 0 if self.image_list else -1
        self.preload_images()

    def preload_images(self):
        self.preloaded_images.clear()
        start = max(0, self.current_index - 3)
        end = min(len(self.image_list), self.current_index + 4)
        for i in range(start, end):
            if i not in self.preloaded_images:
                image_path = os.path.join(self.input_folder, self.image_list[i])
                self.preloaded_images[i] = QPixmap(image_path)

    def get_current_image_path(self):
        if 0 <= self.current_index < len(self.image_list):
            return Path(self.input_folder, self.image_list[self.current_index]).absolute().as_posix()
        return None

    def get_current_image(self):
        self.current_image = self.get_current_image_path()
        
        if self.current_image:
            if self.current_index in self.preloaded_images:
                return self.preloaded_images[self.current_index]
            else:
                return QPixmap(self.current_image)
        return None

    def load_next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            return True
        return False

    def load_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False

    def score_image(self, score, categories):
        if self.current_image:
            current_score, current_categories = self.db.images.get_image_score(self.current_image)
            
            # Update categories
            new_categories = current_categories.copy()
            if isinstance(categories, list):
                for category in categories:
                    if category in new_categories:
                        new_categories.remove(category)
                    else:
                        new_categories.append(category)
            elif isinstance(categories, str):
                if categories in new_categories:
                    new_categories.remove(categories)
                else:
                    new_categories.append(categories)
            
            # Update score
            new_score = score if score else current_score

            if current_score and self.config_handler.get_option('write_to_filesystem'):
                # Image already has a score, update categories and move files if necessary
                if new_score != current_score:
                    # Move the image in the score folder
                    old_score_path = os.path.join(self.output_folder, current_score, os.path.basename(self.current_image))
                    new_score_path = os.path.join(self.output_folder, new_score, os.path.basename(self.current_image))
                    if os.path.exists(old_score_path):
                        create_directory(os.path.dirname(new_score_path))
                        shutil.move(old_score_path, new_score_path)
                    else:
                        # If the image doesn't exist in the old score folder, copy from source
                        create_directory(os.path.dirname(new_score_path))
                        shutil.copy2(self.current_image, new_score_path)

                # Handle category changes
                for category in set(current_categories + new_categories):
                    old_path = os.path.join(self.output_folder, current_score, category, os.path.basename(self.current_image))
                    new_path = os.path.join(self.output_folder, new_score, category, os.path.basename(self.current_image))
                    
                    if category in current_categories and category in new_categories:
                        # Category unchanged, just move the file if score changed
                        if new_score != current_score and os.path.exists(old_path):
                            create_directory(os.path.dirname(new_path))
                            shutil.move(old_path, new_path)
                    elif category in current_categories and category not in new_categories:
                        # Category removed, delete the file
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    elif category not in current_categories and category in new_categories:
                        # Category added, copy the file
                        create_directory(os.path.dirname(new_path))
                        shutil.copy2(self.current_image, new_path)
                
                # Remove old score folder if empty
                if new_score != current_score:
                    old_score_folder = os.path.join(self.output_folder, current_score)
                    if os.path.exists(old_score_folder) and not os.listdir(old_score_folder):
                        os.rmdir(old_score_folder)
            elif new_score and self.config_handler.get_option('write_to_filesystem'):
                # Image doesn't have a score, but now we're adding one
                dest_folder = os.path.join(self.output_folder, new_score)
                self.copy_image_to_folder(dest_folder)  # Copy to score folder
                for category in new_categories:
                    category_folder = os.path.join(dest_folder, category)
                    self.copy_image_to_folder(category_folder)
            else:
                # No score, just updating categories in the database
                pass

            # Update database
            self.db.images.add_or_update_score(self.current_image, new_score, new_categories)
            
            return True
        return False

    def copy_image_to_folder(self, dest_folder):
        create_directory(dest_folder)
        dest_file = os.path.join(dest_folder, os.path.basename(self.current_image))
        shutil.copy2(self.current_image, dest_file)

    def remove_image_file(self, score):
        if score:
            dest_file = os.path.join(self.output_folder, score, os.path.basename(self.current_image))
            if os.path.exists(dest_file):
                os.remove(dest_file)

    def set_output_folder(self, folder):
        self.output_folder = folder

    def get_orientation(self):
        try:
            image = Image.open(self.get_current_image_path())
            exif = image._getexif()

            if exif is not None:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "Orientation":
                        if value == 1:
                            return "Normal"
                        elif value == 3:
                            return "Rotate 180"
                        elif value == 6:
                            return "Rotate 90 CW"
                        elif value == 8:
                            return "Rotate 270 CW"
                        else:
                            return f"Unknown orientation: {value}"
            
            return "No orientation data found"
        
        except Exception as e:
            print(f"Error reading EXIF data: {e}")
            return "Error reading orientation"
        finally:
            if 'image' in locals():
                image.close()
    def get_index(self):
        return self.current_index
    
    def set_index(self, index):
        self.current_index = index

    def get_progress(self):
        if self.image_list:
            return (self.current_index + 1, len(self.image_list))
        return (0, 0)
