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
            tag_group = TagGroup(*row)
            tag_groups.append(tag_group)
            group_mapping[tag_group.id] = len(tag_groups) - 1
        
        # Then get all tags for these groups
        if tag_groups:
            cursor.execute("""
                SELECT tag_id, tag_name, display_order
                FROM tags
                WHERE group_id IN ({})
                ORDER BY display_order
            """.format(','.join('?' * len(tag_groups))), 
            tuple(group.id for group in tag_groups))
            
            # Group tags by their tag_group_id
            for row in cursor.fetchall():
                group_id, tag_name, tag_order = row
                group_idx = group_mapping[group_id]
                tag_groups[group_idx].add_tags([(tag_name, tag_order)])
        
        cursor.close()
        return tag_groups
        