from dataclasses import dataclass
from os import path
from pathlib import Path
from typing import List, Self, Set

from src.config_handler import ConfigHandler


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
class ExportImage:
    id: int
    source_path: str
    dest_path: str
    score: str
    categories: List[str]
    
    def __init__(self, id: int, source_path: str, dest_path: str, score: str, categories: List[str]):
        self.id = id
        self.source_path = source_path
        self.dest_path = dest_path
        self.score = score
        self.categories = categories

    def apply_rule(self, rule: ExportRule, output_dir, seperate_by_score: bool, config: ConfigHandler) -> Self:
        
        return ExportImage(
            id=self.id,
            source_path=self.source_path,
            dest_path=self.create_path(rule, output_dir, seperate_by_score, config),
            score=self.score,
            categories=self.categories
        )
    
    def create_path(self, rule: ExportRule, output_dir, seperate_by_score: bool, config: ConfigHandler) -> str:
        filename = Path(self.source_path).name
        _, scores = config.get_scores()
        if seperate_by_score:
            return path.abspath(path.join(output_dir, scores[self.score], rule.destination, filename))
        else:
            return path.abspath(path.join(output_dir, rule.destination, filename))