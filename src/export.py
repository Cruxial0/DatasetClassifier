
from dataclasses import dataclass
import glob
from os import path
import os
from pathlib import Path
import shutil
from typing import List, Set, Self

@dataclass
class ExportRule:
    categories: Set[str]
    destination: str
    priority: int

    def match(self, categories: Set[str]) -> bool:
        if self.categories is None:
            return True
        return self.categories.issubset(categories)


@dataclass
class Image:
    id: int
    source_path: str
    dest_path: str
    score: str
    categories: List[str]

    def apply_rule(self, rule: ExportRule, output_dir, seperate_by_score: bool) -> Self:
        
        return Image(
            id=self.id,
            source_path=self.source_path,
            dest_path=self.create_path(rule, output_dir, seperate_by_score),
            score=self.score,
            categories=self.categories
        )
    
    def create_path(self, rule: ExportRule, output_dir, seperate_by_score: bool) -> str:
        filename = Path(self.source_path).name
        if seperate_by_score:
            return path.abspath(path.join(output_dir, self.score, rule.destination, filename))
        else:
            return path.abspath(path.join(output_dir, rule.destination, filename))
    

class Exporter:
    def __init__(self, data):
        self.output_dir = data['output_directory']
        self.export_rules = data['rules']
        self.scores = data['scores']
        self.seperate_by_score = data['seperate_by_score']
        self.export_captions = data['export_captions']
        self.export_images = []
        self.failed_exports = 0

    def process_export(self, images: List[Image]) -> dict[str, int]:
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

    def process_images(self, images: List[Image]) -> List[Image]:
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
            
            if not self.export_captions:
                continue
                
            # Handle caption/txt files
            source_stem = os.path.splitext(img.source_path)[0]
            dest_stem = os.path.splitext(img.dest_path)[0]
            
            caption_extensions = ['.caption', '.txt']
            
            for ext in caption_extensions:
                source_caption = Path(f"{source_stem}{ext}")
                dest_caption = Path(f"{dest_stem}{ext}")
                if source_caption.exists():
                    shutil.copy(source_caption, dest_caption)
    
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
        return os.listdir(self.output_dir) == 0

    def match_rule(self, image: Image) -> Image:
        for rule in sorted(self.export_rules, key=lambda x: x.priority, reverse=True):
            if not rule.match(set(image.categories)): continue
            return image.apply_rule(rule, self.output_dir, self.seperate_by_score)
        print(f"WARNING: Could not match any rules for image: {image}")
        self.failed_exports += 1