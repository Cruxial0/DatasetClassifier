from dataclasses import dataclass

@dataclass
class Tag:
    def __init__(self, id: int, name: str, order: int):
        self.id = id
        self.name = name
        self.display_order = order


@dataclass
class TagGroup:
    def __init__(self, id: int, project_id: int, name: str, order: int, is_required: int = 1, allow_multiple: int = 0, prevent_auto_scroll: int = 0, min_tags: int = 1):
        self.id = id
        self.project_id = project_id
        self.name = name
        self.is_required = bool(is_required)
        self.allow_multiple = bool(allow_multiple)
        self.min_tags = min_tags
        self.tags: list[Tag] = None
        self.prevent_auto_scroll = bool(prevent_auto_scroll)
        self.order = order

    def add_tags(self, tags: list[tuple[int, str, int]]):
        if self.tags is None:
            self.tags = []

        for tag in tags:
            self.tags.append(Tag(tag[0], tag[1], tag[2]))

    def verify_self(self):
        """
        Ensures that the tag group is valid
        """
        if self.tags is None:
            self.tags = []
        
        if self.min_tags < 1:
            self.min_tags = 1

        # Ensure there are no gaps in tags display order
        self.tags.sort(key=lambda x: x.display_order)
        for i in range(len(self.tags) - 1):
            if self.tags[i + 1].display_order - self.tags[i].display_order != 1:
                self.tags[i + 1].display_order = self.tags[i].display_order + 1

    def __repr__(self) -> str:
        return f"TagGroup(id={self.id}, name={self.name}, tags={self.tags}, order={self.order}) {{required:{self.is_required}, allow_multiple:{self.allow_multiple}, min_tags:{self.min_tags}}}"