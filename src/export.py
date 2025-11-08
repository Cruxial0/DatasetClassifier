"""
Updated export.py with proper Set[str] handling for additional_tags

This version ensures that additional_tags are properly added using set operations
and that the apply_rule bug is noted.
"""

import os
from pathlib import Path
import shutil
from typing import List

from src.caption_handler import CaptionHandler
from src.database.database import Database
from src.export_image import ExportImage
from src.config_handler import ConfigHandler
from src.parser import parse_condition, evaluate_condition


class Exporter:
    def __init__(self, data, database: Database, config: ConfigHandler):
        self.config = config
        self.database = database
        self.caption_handler = CaptionHandler(database, config)

        self.output_dir = data['output_directory']
        self.export_rules = data['rules']
        self.scores = data['scores']
        self.seperate_by_score = data['seperate_by_score']
        self.export_captions = data['export_captions']
        self.delete_images = data['delete_images']
        self.apply_tag_rules = data.get('apply_tag_rules', True)
        self.export_images = []
        self.failed_exports = 0

        # Load project tag groups and export tag rules
        self.project_id = data.get('project_id')
        self.tag_groups = []
        self.export_tag_rules = []

        if self.project_id and self.apply_tag_rules:
            self.tag_groups = self.database.tags.get_project_tags(self.project_id)
            self.export_tag_rules = self.database.export_rules.get_project_rules(self.project_id)

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

            # Apply export tag rules to add additional tags
            if self.apply_tag_rules and self.export_tag_rules:
                self._apply_export_tag_rules(img)

            matched_img = self.match_rule(img)
            output.append(matched_img)
        return output

    def _apply_export_tag_rules(self, image: ExportImage):
        """
        Apply export tag rules to an image to add additional tags based on conditions.

        This version properly handles Set[str] for additional_tags.

        Args:
            image: The ExportImage to process
        """
        # if not image.tag_ids:
        #     return

        # Initialize additional_tags as set if None
        if image.additional_tags is None:
            image.additional_tags = set()

        # Get all enabled rules
        enabled_rules = [rule for rule in self.export_tag_rules if rule.enabled]

        for rule in enabled_rules:
            try:
                # Parse the rule condition
                parsed_condition = parse_condition(rule.condition)

                if parsed_condition is None:
                    print(f"Warning: Empty condition for rule '{rule.name}'")
                    continue

                # Evaluate the condition against the image's tags
                condition_met = evaluate_condition(
                    parsed_condition,
                    image.tag_ids,
                    self.tag_groups
                )

                # If condition is met, add the tags
                if condition_met:
                    for tag_to_add in rule.tags_to_add:
                        # Use set.add() for Set[str]
                        image.additional_tags.add(tag_to_add)
                        print(f"Rule '{rule.name}': Added tag '{tag_to_add}' to image {image.id}")

            except Exception as e:
                print(f"Error applying export tag rule '{rule.name}': {e}")

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

            # Collect captions (including additional tags from export rules)
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
        """
        Match image to export rule and return modified image.


        Args:
            image: Original ExportImage with additional_tags populated by rules

        Returns:
            New ExportImage with dest_path set and fields copied
        """
        for rule in sorted(self.export_rules, key=lambda x: x.priority, reverse=True):
            if not rule.match(set(image.categories)):
                continue

            return image.apply_rule(rule, self.output_dir, self.seperate_by_score, self.config)

        print(f"WARNING: Could not match any rules for image: {image}")
        self.failed_exports += 1
        return image
