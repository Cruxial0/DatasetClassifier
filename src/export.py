
from dataclasses import dataclass
import glob
from os import path
import os
from pathlib import Path
import shutil
from typing import List, Set, Self

from src.caption_handler import CaptionHandler
from src.database.database import Database
from src.export_image import ExportImage
from src.config_handler import ConfigHandler
    

class Exporter:
    def __init__(self, data, database: Database, config: ConfigHandler):
        self.config = config
        self.caption_handler = CaptionHandler(database, config)

        self.output_dir = data['output_directory']
        self.export_rules = data['rules']
        self.scores = data['scores']
        self.seperate_by_score = data['seperate_by_score']
        self.export_captions = data['export_captions']
        self.delete_images = data['delete_images']
        self.export_images = []
        self.failed_exports = 0

    def process_export(self, images: List[ExportImage]) -> dict[str, int]:
        self.export_images = self.process_images(images)

        found_dirs = dict()

        for img in self.export_images:
            path = str(Path(img.dest_path).parent.relative_to(self.output_dir))
            if path == '.':
                path = "./"
            elif not path.startswith('.'):
                path = f"./{path}"
            if not path in found_dirs.keys():
                found_dirs[path] = 1
            else:
                found_dirs[path] += 1

        return found_dirs

    def process_images(self, images: List[ExportImage]) -> List[ExportImage]:
        output = []
        for img in images:
            if not img.score in self.scores:
                continue
            output.append(self.match_rule(img))
        return output
    
    def export(self):
        self.clean_output_dir()
        for img in self.export_images:
            # Create destination directory and copy image
            dest_dir = Path(img.dest_path).parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(img.source_path, img.dest_path)
            
            if self.delete_images:
                os.remove(img.source_path)
            
            if not self.export_captions:
                continue
            
            # Collect captions
            self.caption_handler.collect_image_captions(img)

        self.caption_handler.write_image_captions()
    
    def clean_output_dir(self):
        # Sourced from https://stackoverflow.com/a/185941
        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def output_dir_empty(self) -> bool:
        return len(os.listdir(self.output_dir)) == 0

    def match_rule(self, image: ExportImage) -> ExportImage:
        for rule in sorted(self.export_rules, key=lambda x: x.priority, reverse=True):
            if not rule.match(set(image.categories)): continue
            return image.apply_rule(rule, self.output_dir, self.seperate_by_score, self.config)
        print(f"WARNING: Could not match any rules for image: {image}")
        self.failed_exports += 1