from dataclasses import dataclass, field
from typing import List, Set

@dataclass
class ExportCondition:
    """
    Represents a condition-based rule for adding tags during export.

    When the condition is met, the specified tags will be added to the image's caption.
    """
    id: int
    project_id: int
    name: str
    condition: str  # Uses the same syntax as TagGroup activation conditions
    tags_to_add: List[str]  # Tags to add when condition is met
    priority: int = 0  # Higher priority rules are evaluated first
    enabled: bool = True

    def __post_init__(self):
        """Ensure tags_to_add is always a list"""
        if isinstance(self.tags_to_add, str):
            self.tags_to_add = [tag.strip() for tag in self.tags_to_add.split(',')]


@dataclass
class ExportConditionResult:
    """Result of evaluating export conditions for an image"""
    image_id: int
    original_tags: Set[str]
    added_tags: Set[str] = field(default_factory=set)
    applied_conditions: List[str] = field(default_factory=list)  # Names of applied conditions

    def get_all_tags(self) -> Set[str]:
        """Get combined original and added tags"""
        return self.original_tags | self.added_tags

    def add_tags(self, tags: List[str], condition_name: str):
        """Add tags from a condition"""
        self.added_tags.update(tags)
        self.applied_conditions.append(condition_name)
