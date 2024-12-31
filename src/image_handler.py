import os
from pathlib import Path
import shutil
from PyQt6.QtGui import QPixmap
from PIL import Image
from PIL.ExifTags import TAGS
from src.database.database import Database
from src.utils import create_directory

class ImageHandler:
    """
    Handles image loading, navigation, and scoring for a project-based image management system.
    Works with a database to maintain project-specific image collections and scoring data.
    """
    def __init__(self, db: Database, config_handler):
        """
        Initialize the ImageHandler with database and configuration.
        
        Args:
            db: Database instance for storing image and project data
            config_handler: Configuration handler for system settings
        """
        self.db = db
        self.config_handler = config_handler
        self.current_project_id = None
        self.output_folder = None
        self.image_ids = []
        self.current_image_id = None
        self.preloaded_images = {}
        self.path_cache = {}  # Cache for image paths
        self.score_cache = {}  # Cache for image scores
        self.cache_size = 100  # Number of items to keep in cache
        

    def set_db(self, db: Database):
        """Update the database instance."""
        self.db = db
        

    def set_output_folder(self, folder: str):
        """Set the output folder for scored images."""
        self.output_folder = folder


    def load_images(self, project_id: int, hide_scored_images: bool = False, get_scored_only: bool = False):
        """Load images with optimized database query"""
        self.current_project_id = project_id

        if hide_scored_images and get_scored_only:
            raise ValueError("Cannot hide scored images and get only scored images at the same time.")
        
        # Get image IDs and paths in a single query
        if hide_scored_images:
            query = """
                SELECT DISTINCT i.image_id, i.source_path, s.score, s.categories 
                FROM images i 
                LEFT JOIN scores s ON i.image_id = s.image_id AND i.project_id = s.project_id
                WHERE i.project_id = ? 
                AND s.image_id IS NULL
                ORDER BY i.image_id
            """
        elif get_scored_only:
            query = """
                SELECT DISTINCT i.image_id, i.source_path, s.score, s.categories 
                FROM images i 
                LEFT JOIN scores s ON i.image_id = s.image_id AND i.project_id = s.project_id
                WHERE i.project_id = ? 
                AND s.image_id IS NOT NULL
                AND s.score IS NOT NULL
                AND s.score != 'discard'
                ORDER BY i.image_id
            """
        else:
            query = """
                SELECT DISTINCT i.image_id, i.source_path,
                       (SELECT score FROM scores WHERE image_id = i.image_id AND project_id = i.project_id LIMIT 1) as score,
                       (SELECT categories FROM scores WHERE image_id = i.image_id AND project_id = i.project_id LIMIT 1) as categories
                FROM images i 
                WHERE i.project_id = ?
                ORDER BY i.image_id
            """
            
        cursor = self.db.connection.cursor()
        results = cursor.execute(query, (project_id,)).fetchall()
        
        self.image_ids = []
        self.path_cache.clear()
        self.score_cache.clear()
        
        for row in results:
            image_id = row[0]
            self.image_ids.append(image_id)
            self.path_cache[image_id] = row[1]
            self.score_cache[image_id] = (row[2], row[3] if row[3] else [])

        self.current_image_id = self.image_ids[0] if self.image_ids else None
        self.preload_images()


    def preload_images(self):
        """Preload images with optimized memory management"""
        if not self.current_image_id:
            return

        try:
            current_idx = self.image_ids.index(self.current_image_id)
        except ValueError:
            return

        # Clear old preloaded images outside the window
        keep_ids = set()
        start = max(0, current_idx - 3)
        end = min(len(self.image_ids), current_idx + 4)
        
        for i in range(start, end):
            keep_ids.add(self.image_ids[i])
        
        # Remove images that are no longer needed
        self.preloaded_images = {
            k: v for k, v in self.preloaded_images.items() 
            if k in keep_ids
        }

        # Preload new images
        for i in range(start, end):
            image_id = self.image_ids[i]
            if image_id not in self.preloaded_images:
                image_path = self.path_cache.get(image_id)
                if image_path:
                    try:
                        self.preloaded_images[image_id] = QPixmap(image_path)
                    except Exception as e:
                        print(f"Error preloading image {image_id}: {e}")

    def get_current_image_path(self) -> str | None:
        """Get image path from cache"""
        if self.current_image_id is None:
            return None
        return self.path_cache.get(self.current_image_id)


    def get_current_image(self) -> QPixmap | None:
        """Get image with cache priority"""
        if not self.current_image_id:
            return None
            
        # Try to get from preloaded cache first
        pixmap = self.preloaded_images.get(self.current_image_id)
        if pixmap:
            return pixmap
        
        # Load if not in cache
        image_path = self.get_current_image_path()
        if image_path:
            try:
                pixmap = QPixmap(image_path)
                self.preloaded_images[self.current_image_id] = pixmap
                return pixmap
            except Exception as e:
                print(f"Error loading image: {e}")
        return None


    def load_next_image(self) -> bool:
        """Move to the next image in the sequence."""
        if not self.image_ids or self.current_image_id is None:
            return False
            
        current_idx = self.image_ids.index(self.current_image_id)
        if current_idx < len(self.image_ids) - 1:
            self.current_image_id = self.image_ids[current_idx + 1]
            self.preload_images()
            return True
        return False


    def load_previous_image(self) -> bool:
        """Move to the previous image in the sequence."""
        if not self.image_ids or self.current_image_id is None:
            return False
            
        current_idx = self.image_ids.index(self.current_image_id)
        if current_idx > 0:
            self.current_image_id = self.image_ids[current_idx - 1]
            self.preload_images()
            return True
        return False

    def previous_image_exists(self) -> bool:
        if not self.image_ids or self.current_image_id is None:
            return False
        return self.image_ids.index(self.current_image_id) > 0
    
    def next_image_exists(self) -> bool:
        if not self.image_ids or self.current_image_id is None:
            return False
        return self.image_ids.index(self.current_image_id) < len(self.image_ids) - 1
    
    def load_image_from_raw_id(self, image_id: int) -> bool:
        if image_id in self.image_ids:
            idx = self.image_ids.index(image_id) - 1
            self.current_image_id = self.image_ids[idx]
            self.preload_images()
            return True
        return False
    
    def get_absolute_index(self) -> int:
        if not self.image_ids or self.current_image_id is None:
            return -1
        return self.image_ids.index(self.current_image_id)

    def get_score(self, image_path: str) -> tuple[str | None, list[str]]:
        """Get score from cache if available"""
        if self.current_image_id is None:
            return None, []
        
        # Try cache first
        if self.current_image_id in self.score_cache:
            return self.score_cache[self.current_image_id]
        
        # Fall back to database
        score, categories = self.db.images.get_score(image_path)
        self.score_cache[self.current_image_id] = (score, categories)
        return score, categories


    def score_image(self, score: int | None, categories: list[str] | str) -> bool:
        """
        Score the current image and update its categories.
        
        Args:
            score: Numeric score for the image
            categories: List of categories or single category to toggle
            
        Returns:
            bool: True if scoring succeeded, False otherwise
        """
        image_path = self.get_current_image_path()
        if not image_path:
            return False
            
        current_score, current_categories = self.get_score(image_path)
        if type(current_categories) is not list:
            current_categories = []

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
        new_score = score if score is not None else current_score
            
        # Try to update database
        try:
            if self.db.images.add_or_update_score(image_path, new_score, new_categories):
                # Update the cache immediately after successful database update
                if self.current_image_id is not None:
                    self.score_cache[self.current_image_id] = (new_score, new_categories)
                return True
            return False
        except Exception as e:
            print(f"Error in score_image: {e}")
            return False


    def get_orientation(self) -> str:
        """Get the EXIF orientation of the current image."""
        image_path = self.get_current_image_path()
        if not image_path:
            return "No image loaded"
            
        try:
            with Image.open(image_path) as image:
                exif = image._getexif()
                if not exif:
                    return "No orientation data found"
                    
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "Orientation":
                        return {
                            1: "Normal",
                            3: "Rotate 180",
                            6: "Rotate 90 CW",
                            8: "Rotate 270 CW"
                        }.get(value, f"Unknown orientation: {value}")
                        
            return "No orientation data found"
            
        except Exception as e:
            print(f"Error reading EXIF data: {e}")
            return "Error reading orientation"


    def get_progress(self) -> tuple[int, int]:
        """Get the current position and total count of images."""
        if not self.image_ids or self.current_image_id is None:
            return (0, 0)
            
        current_idx = self.image_ids.index(self.current_image_id)
        return (current_idx + 1, len(self.image_ids))


    def get_index(self) -> int:
        """Get the current image index."""
        if not self.image_ids or self.current_image_id is None:
            return -1
        return self.image_ids.index(self.current_image_id)
    

    def set_index(self, index: int):
        """Set the current image index."""
        if 0 <= index < len(self.image_ids):
            self.current_image_id = self.image_ids[index]
            self.preload_images()