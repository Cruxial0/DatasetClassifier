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

    def score_image(self, score, default_scores):
        if self.current_image and self.output_folder:
            is_category = score not in default_scores
            current_scores = self.db.get_image_scores(self.current_image)
            
            if score in current_scores:
                self.db.remove_score(self.current_image, score)
                self.remove_image_file(score, default_scores)
            else:
                if is_category:
                    self.handle_category_scoring(score, current_scores, default_scores)
                else:
                    self.handle_default_scoring(score, current_scores, default_scores)

            return True
        return False

    def handle_category_scoring(self, category, current_scores, default_scores):
        if self.config_handler.get_treat_categories_as_scoring():
            dest_folder = os.path.join(self.output_folder, category)
        else:
            default_score = next((score for score in current_scores if score in default_scores), default_scores[0])
            dest_folder = os.path.join(self.output_folder, default_score, category)

        self.copy_image_to_folder(dest_folder)
        self.db.add_score(self.current_image, os.path.join(dest_folder, os.path.basename(self.current_image)), category)

    def handle_default_scoring(self, score, current_scores, default_scores):
        dest_folder = os.path.join(self.output_folder, score)
        self.copy_image_to_folder(dest_folder)
        self.db.add_score(self.current_image, os.path.join(dest_folder, os.path.basename(self.current_image)), score)

        for old_score in current_scores:
            if old_score in default_scores:
                self.remove_image_file(old_score, default_scores)
                self.db.remove_score(self.current_image, old_score)
            else:  # It's a category
                if not self.config_handler.get_treat_categories_as_scoring():
                    old_default_score = next((s for s in current_scores if s in default_scores), None)
                    if old_default_score:
                        old_category_folder = os.path.join(self.output_folder, old_default_score, old_score)
                        new_category_folder = os.path.join(dest_folder, old_score)
                        old_image_path = os.path.join(old_category_folder, os.path.basename(self.current_image))
                        new_image_path = os.path.join(new_category_folder, os.path.basename(self.current_image))
                        
                        if os.path.exists(old_image_path):
                            create_directory(new_category_folder)
                            shutil.move(old_image_path, new_image_path)
                        
                        self.db.update_score(self.current_image, old_score, new_image_path)

    def copy_image_to_folder(self, dest_folder):
        create_directory(dest_folder)
        dest_file = os.path.join(dest_folder, os.path.basename(self.current_image))
        shutil.copy2(self.current_image, dest_file)

    def remove_image_file(self, score, default_scores):
        if self.config_handler.get_treat_categories_as_scoring() or score in default_scores:
            dest_file = os.path.join(self.output_folder, score, os.path.basename(self.current_image))
        else:
            default_score = next((s for s in self.db.get_image_scores(self.current_image) if s in default_scores), default_scores[0])
            dest_file = os.path.join(self.output_folder, default_score, score, os.path.basename(self.current_image))
        
        if os.path.exists(dest_file):
            os.remove(dest_file)

    def set_output_folder(self, folder):
        self.output_folder = folder

    def get_progress(self):
        if self.image_list:
            return (self.current_index + 1, len(self.image_list))
        return (0, 0)
