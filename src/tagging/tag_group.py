from dataclasses import dataclass, field
from typing import List, Optional
from src.parser import parse_condition, validate_references

@dataclass
class Tag:
    id: int
    name: str
    display_order: int

@dataclass
class TagGroup:
    id: int
    project_id: int
    name: str
    order: int
    is_required: bool = True
    allow_multiple: bool = False
    min_tags: int = 1
    prevent_auto_scroll: bool = False
    tags: List[Tag] = field(default_factory=list)
    condition: Optional[str] = None 

    def add_tags(self, tags: List[tuple[int, str, int]]):
        for tag in tags:
            self.tags.append(Tag(tag[0], tag[1], tag[2]))

    def get_tag(self, tag_id: int) -> Optional[Tag]:
        for tag in self.tags:
            if tag.id == tag_id:
                return tag
        return None

    def verify_self(self, all_groups: List['TagGroup'] = None):
        """
        Ensures that the tag group is valid, including condition validation.
        :param all_groups: Optional list of all tag groups in the project for cross-validation.
        """

        if self.min_tags < 1:
            self.min_tags = 1

        # Sort tags by display_order and fix gaps
        self.tags.sort(key=lambda x: x.display_order)
        for i in range(len(self.tags) - 1):
            if self.tags[i + 1].display_order - self.tags[i].display_order != 1:
                self.tags[i + 1].display_order = self.tags[i].display_order + 1

        # Validate condition if provided (and all_groups is given for context)
        if self.condition and all_groups:
            try:
                # Parse to validate syntax
                parsed = parse_condition(self.condition)
                # Validate references: ensure groups/tags exist and are prior
                validate_references(parsed, self, all_groups)
            except ValueError as e:
                raise ValueError(f"Invalid condition for group '{self.name}': {e}")

    def __repr__(self) -> str:
        return (f"TagGroup(id={self.id}, name={self.name}, tags={self.tags}, order={self.order}) "
                f"{{required:{self.is_required}, allow_multiple:{self.allow_multiple}, min_tags:{self.min_tags}, "
                f"condition:{self.condition}}}")