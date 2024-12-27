from sqlite3 import Connection

from src.tagging.tag_group import TagGroup, Tag


class TagQueries:
    def __init__(self, db: Connection):
        self.db = db

    def get_project_tags(self, project_id: int) -> list[TagGroup]:
        """
        Get all tag groups for the given project id from the database. The result will be a list of TagGroups, each containing a list of Tags.

        Args:
            project_id (int): The id of the project to query.

        Returns:
            list[TagGroup]: A list of TagGroups, each containing a list of Tags.
        """
        cursor = self.db.cursor()
        
        # First, get all tag groups for the project
        cursor.execute("""
            SELECT group_id, project_id, group_name, is_required, allow_multiple, min_tags, display_order
            FROM tag_groups
            WHERE project_id = ?
            ORDER BY display_order
        """, (project_id,))
        
        tag_groups = []
        group_mapping = {}  # Maps group_id to its index in tag_groups list
        
        # Create TagGroup objects
        for row in cursor.fetchall():
            tag_group = TagGroup(
                id=row[0],
                project_id=row[1],
                name=row[2],
                order=row[6],  # display_order is at index 6
                is_required=row[3],
                allow_multiple=row[4],
                min_tags=row[5]
            )
            tag_groups.append(tag_group)
            group_mapping[tag_group.id] = len(tag_groups) - 1
        
        # Then get all tags for these groups
        if tag_groups:
            cursor.execute("""
                SELECT tag_id, group_id, tag_name, display_order
                FROM tags
                WHERE group_id IN ({})
                ORDER BY display_order
            """.format(','.join('?' * len(tag_groups))), 
            tuple(group.id for group in tag_groups))
            
            # Group tags by their tag_group_id
            for row in cursor.fetchall():
                tag_id, group_id, tag_name, tag_order = row
                group_idx = group_mapping[group_id]
                tag_groups[group_idx].add_tags([(tag_id, tag_name, tag_order)])

        cursor.close()
        return tag_groups
    
    def get_tag_group(self, group_id: int) -> TagGroup:
        """
        Gets the tag group with the given id from the database, alongside its tags.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT group_id, project_id, group_name, is_required, allow_multiple, min_tags, display_order FROM tag_groups WHERE group_id = ?", (group_id,))
        group = TagGroup(*cursor.fetchone())
        cursor.execute("SELECT tag_id, tag_name, display_order FROM tags WHERE group_id = ?", (group_id,))
        for row in cursor.fetchall():
            tag_id, tag_name, tag_order = row
            group.add_tags([(tag_id, tag_name, tag_order)])
        cursor.close()
        return group
        
    def add_tag(self, name: str, group_id: int, order: int) -> int:
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO tags (group_id, tag_name, display_order) VALUES (?, ?, ?)", (group_id, name, order))
        self.db.commit()

        last_id = cursor.lastrowid
        cursor.close()

        return last_id

    def add_tag_group(self, name: str, order: int, project_id: int) -> int:
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO tag_groups (project_id, group_name, display_order) VALUES (?, ?, ?)", (project_id, name, order))
        self.db.commit()

        last_id = cursor.lastrowid
        cursor.close()

        return last_id

    def update_tag(self, tag: Tag):
        cursor = self.db.cursor()
        cursor.execute("UPDATE tags SET tag_name = ?, display_order = ? WHERE tag_id = ?", (tag.name, tag.display_order, tag.id))
        self.db.commit()
        cursor.close()

    def update_tag_group(self, tag_group: TagGroup):
        cursor = self.db.cursor()
        cursor.execute("UPDATE tag_groups SET group_name = ?, display_order = ?, is_required = ?, allow_multiple = ?, min_tags = ? WHERE group_id = ?", 
            (tag_group.name, tag_group.order, tag_group.is_required, tag_group.allow_multiple, tag_group.min_tags, tag_group.id))
        self.db.commit()
        cursor.close()

    def update_tag_order(self, new_order: list[tuple[int, int]]):
        cursor = self.db.cursor()
        cursor.executemany("UPDATE tags SET display_order = ? WHERE tag_id = ?", [(order[1], order[0]) for order in new_order])
        self.db.commit()
        cursor.close()

    def update_tag_group_order(self, new_order: list[tuple[int, int]]):
        cursor = self.db.cursor()
        cursor.executemany("UPDATE tag_groups SET display_order = ? WHERE group_id = ?", [(order[1], order[0]) for order in new_order])
        self.db.commit()
        cursor.close()

    def delete_tag(self, tag_id: int):
        cursor = self.db.cursor()

        # Tag deletion is cascaded, so we only need to delete the tag
        # All image tags will be deleted automatically
        cursor.execute("DELETE FROM tags WHERE tag_id = ?", (tag_id,))
        self.db.commit()
        cursor.close()

    def delete_tag_group(self, group_id: int):
        cursor = self.db.cursor()
        
        # Tag Group deletion is cascaded, so we only need to delete the tag group itself
        # All tags will be deleted automatically
        cursor.execute("DELETE FROM tag_groups WHERE group_id = ?", (group_id,))
        self.db.commit()
        cursor.close()

    def tag_name_exists(self, tag_name: str, group_id: int) -> bool:
        cursor = self.db.cursor()
        cursor.execute("SELECT tag_id FROM tags WHERE tag_name = ? AND group_id = ?", (tag_name, group_id))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def tag_group_name_exists(self, group_name: str, project_id: int) -> bool:
        cursor = self.db.cursor()
        cursor.execute("SELECT group_id FROM tag_groups WHERE group_name = ? AND project_id = ?", (group_name, project_id))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def image_has_tag(self, image_id: int, tag_id: int) -> bool:
        cursor = self.db.cursor()
        cursor.execute("SELECT tag_id FROM image_tags WHERE image_id = ? AND tag_id = ?", (image_id, tag_id))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def add_image_tag(self, image_id: int, tag_id: int):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO image_tags (image_id, tag_id) VALUES (?, ?)", (image_id, tag_id))
        self.db.commit()
        cursor.close()

    def delete_image_tag(self, image_id: int, tag_id: int):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM image_tags WHERE image_id = ? AND tag_id = ?", (image_id, tag_id))
        self.db.commit()
        cursor.close()

    def get_image_tags(self, image_id: int) -> list[int]:
        cursor = self.db.cursor()
        cursor.execute("SELECT tag_id FROM image_tags WHERE image_id = ?", (image_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def get_tags_from_ids(self, tag_id: list[int]) -> list[tuple[int, int, str, int, int]]:
        """Returns a list of tuples of tag_id and tag_name for the given list of tag_ids."""
        cursor = self.db.cursor()
        # Get the following values from the tags table: tag_id, group_id, tag_name, display_order
        # Aditionally, get the display_order from the tag_groups table
        cursor.execute(
            """
            SELECT tags.tag_id, tags.group_id, tags.tag_name, tags.display_order, tag_groups.display_order
            FROM tags
            JOIN tag_groups ON tags.group_id = tag_groups.group_id
            WHERE tags.tag_id IN ({})
            """.format(','.join('?' * len(tag_id))), tag_id)
        return cursor.fetchall()