from dataclasses import dataclass

@dataclass
class Tag:
    def __init__(self, id: int, name: str, order: int):
        self.id = id
        self.name = name
        self.display_order = order


@dataclass
class TagGroup:
    def __init__(self, id: int, project_id: int, name: str, order: int, is_required: bool = False, allow_multiple: bool = False, min_tags: int = 0):
        self.id = id
        self.project_id = project_id
        self.name = name
        self.is_required = is_required
        self.allow_multiple = allow_multiple
        self.min_tags = min_tags
        self.tags: list[Tag] = None
        self.order = order

    def add_tags(self, tags: list[tuple[int, str, int]]):
        if self.tags is None:
            self.tags = []

        for tag in tags:
            self.tags.append(Tag(tag[0], tag[1], tag[2]))