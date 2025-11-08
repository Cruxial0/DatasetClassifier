from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import os
from src.export_image import ExportImage
from src.config_handler import ConfigHandler
from src.database.database import Database

@dataclass
class Caption():
    def __init__(self, tag_id: int, group_id: int, tag_name: str, tag_order: int, group_order: int):
        self.tag_id = tag_id
        self.group_id = group_id
        self.tag_name = tag_name
        self.tag_order = tag_order
        self.group_order = group_order

class CaptionHandler():
    def __init__(self, database: Database, config_handler: ConfigHandler):
        self.db = database
        self.config_handler = config_handler

        self.image_captions: dict[str, str] = {}

    def collect_image_captions(self, image: ExportImage):
        """
        Collect captions for an image from both database tags and additional tags
        added by export tag rules.
        
        Args:
            image: ExportImage with database tags and potentially additional_tags from rules
        """
        caption_parts = []
        
        # First, get all tag_ids from the database
        image_tag_ids = self.db.tags.get_image_tags(image.id)

        if len(image_tag_ids) > 0:
            captions: list[Caption] = []

            # Get tag details from tag_ids
            for caption in self.db.tags.get_tags_from_ids(image_tag_ids):
                captions.append(Caption(*caption))

            # Sort captions by group_order, then tag_order
            captions.sort(key=lambda x: (x.group_order, x.tag_order))
            
            # Add database tags to caption parts
            caption_parts.extend([caption.tag_name for caption in captions])
        
        # Add additional tags from export tag rules (if any)
        # Handle both Set[str] and List[str] types
        if hasattr(image, 'additional_tags') and image.additional_tags:
            # Convert set to sorted list for consistent ordering
            if isinstance(image.additional_tags, set):
                additional = sorted(image.additional_tags)
            else:
                additional = list(image.additional_tags)
            
            caption_parts.extend(additional)
        
        # Only create a caption entry if there are any tags
        if caption_parts:
            self.image_captions[image.dest_path] = ', '.join(caption_parts)


    def write_single_caption(self, image_path, caption):
        with open(image_path, 'w') as f:
            f.write(caption)

    def write_image_captions(self):
        file_extension = self.config_handler.get_value('export_options.caption_format')
        # Create all paths first
        file_tasks = [
            (f'{"".join(dest_path.split(".")[0:-1])}{file_extension}', caption)
            for dest_path, caption in self.image_captions.items()
        ]
        
        # Ensure all directories exist first (once per directory)
        directories = {os.path.dirname(path) for path, _ in file_tasks}
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Write files in parallel
        with ThreadPoolExecutor() as executor:
            executor.map(lambda x: self.write_single_caption(*x), file_tasks)