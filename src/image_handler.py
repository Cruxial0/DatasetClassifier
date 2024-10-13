import os
import shutil
from PyQt6.QtGui import QPixmap
from src.utils import create_directory

class ImageHandler:
    def __init__(self, db, config_handler):
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
        self.image_list = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if hide_scored_images:
            self.image_list = [img for img in self.image_list if not self.db.is_image_scored(os.path.join(self.input_folder, img))]
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
            return os.path.join(self.input_folder, self.image_list[self.current_index])
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
        if self.current_image and self.output_folder:
            current_score, current_categories = self.db.get_image_score(self.current_image)
            
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
            dest_path = os.path.join(self.output_folder, new_score, os.path.basename(self.current_image)) if new_score else None
            self.db.add_or_update_score(self.current_image, dest_path, new_score, new_categories)
            
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

    def get_progress(self):
        if self.image_list:
            return (self.current_index + 1, len(self.image_list))
        return (0, 0)

    def sync_filesystem_with_database(self):
        all_scores = self.db.get_all_scores()
        for source_path, dest_path, score, categories in all_scores:
            if not os.path.exists(source_path):
                self.db.remove_score(source_path)
            elif not os.path.exists(dest_path):
                dest_folder = os.path.join(self.output_folder, score, *categories)
                new_dest_path = os.path.join(dest_folder, os.path.basename(source_path))
                self.copy_image_to_folder(dest_folder)
                self.db.add_or_update_score(source_path, new_dest_path, score, categories)
