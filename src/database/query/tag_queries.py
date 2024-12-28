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
            SELECT group_id, project_id, group_name, is_required, allow_multiple, min_tags, prevent_auto_scroll, display_order
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
                order=row[7],  # display_order is at index 7
                is_required=row[3],
                allow_multiple=row[4],
                min_tags=row[5],
                prevent_auto_scroll=row[6]
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
        cursor.execute("SELECT group_id, project_id, group_name, is_required, allow_multiple, min_tags, prevent_auto_scroll, display_order FROM tag_groups WHERE group_id = ?", (group_id,))
        result = cursor.fetchone()
        group = TagGroup(
                id=result[0],
                project_id=result[1],
                name=result[2],
                order=result[7],  # display_order is at index 6
                is_required=result[3],
                allow_multiple=result[4],
                min_tags=result[5], 
                prevent_auto_scroll=result[6]
            )
        cursor.execute("SELECT tag_id, tag_name, display_order FROM tags WHERE group_id = ?", (group_id,))
        for row in cursor.fetchall():
            tag_id, tag_name, tag_order = row
            group.add_tags([(tag_id, tag_name, tag_order)])
        cursor.close()
        return group
        
    def add_tag(self, name: str, group_id: int, order: int) -> int:
        """
        Adds a new tag to the specified group in the database.

        Args:
            name (str): The name of the tag to add.
            group_id (int): The ID of the group to which the tag belongs.
            order (int): The display order of the tag within the group.

        Returns:
            int: The ID of the newly added tag.
        """

        cursor = self.db.cursor()
        cursor.execute("INSERT INTO tags (group_id, tag_name, display_order) VALUES (?, ?, ?)", (group_id, name, order))
        self.db.commit()

        last_id = cursor.lastrowid
        cursor.close()

        return last_id

    def add_tag_group(self, name: str, order: int, project_id: int) -> int:
        """
        Adds a new tag group to the database with the given name, order, and project_id.

        Args:
            name (str): The name of the tag group to add.
            order (int): The display order of the tag group.
            project_id (int): The id of the project to which the tag group belongs.

        Returns:
            int: The id of the newly added tag group.
        """
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO tag_groups (project_id, group_name, display_order) VALUES (?, ?, ?)", (project_id, name, order))
        self.db.commit()

        last_id = cursor.lastrowid
        cursor.close()

        return last_id

    def update_tag(self, tag: Tag):
        """
        Updates the tag with the given id in the database, with the new tag's fields.

        Args:
            tag (Tag): The tag to update.
        """
        cursor = self.db.cursor()
        cursor.execute("UPDATE tags SET tag_name = ?, display_order = ? WHERE tag_id = ?", (tag.name, tag.display_order, tag.id))
        self.db.commit()
        cursor.close()

    def update_tag_group(self, tag_group: TagGroup):
        """
        Updates the tag group with the given id in the database, with the new tag group's fields.
        """
        cursor = self.db.cursor()
        cursor.execute("UPDATE tag_groups SET group_name = ?, display_order = ?, is_required = ?, allow_multiple = ?, min_tags = ?, prevent_auto_scroll = ? WHERE group_id = ?", 
            (tag_group.name, tag_group.order, tag_group.is_required, tag_group.allow_multiple, tag_group.min_tags, tag_group.prevent_auto_scroll, tag_group.id))
        self.db.commit()
        cursor.close()

    def update_tag_order(self, new_order: list[tuple[int, int]]):
        """
        Updates the display order of all tags in the given list of tuples, where each tuple contains the tag_id and its new display_order.

        Args:
            new_order (list[tuple[int, int]]): The list of tuples, where each tuple contains the tag_id and its new display_order.
        """
        cursor = self.db.cursor()
        cursor.executemany("UPDATE tags SET display_order = ? WHERE tag_id = ?", [(order[1], order[0]) for order in new_order])
        self.db.commit()
        cursor.close()

    def update_tag_group_order(self, new_order: list[tuple[int, int]]):
        """
        Updates the display order of all tag groups in the given list of tuples, where each tuple contains the
        group_id and its new display_order.

        Args:
            new_order (list[tuple[int, int]]): A list of tuples, each containing the group_id and its new display_order.
        """

        cursor = self.db.cursor()
        cursor.executemany("UPDATE tag_groups SET display_order = ? WHERE group_id = ?", [(order[1], order[0]) for order in new_order])
        self.db.commit()
        cursor.close()

    def delete_tag(self, tag_id: int):
        """
        Deletes the tag with the given id from the database.
        """

        cursor = self.db.cursor()

        # Tag deletion is cascaded, so we only need to delete the tag
        # All image tags will be deleted automatically
        cursor.execute("DELETE FROM tags WHERE tag_id = ?", (tag_id,))
        self.db.commit()
        cursor.close()

    def delete_tag_group(self, group_id: int):
        """
        Deletes the tag group with the given id from the database. This will also delete all tags
        in the tag group, as the deletion is cascaded.
        
        Args:
            group_id (int): The id of the tag group to delete.
        """

        cursor = self.db.cursor()
        
        # Tag Group deletion is cascaded, so we only need to delete the tag group itself
        # All tags will be deleted automatically
        cursor.execute("DELETE FROM tag_groups WHERE group_id = ?", (group_id,))
        self.db.commit()
        cursor.close()

    def tag_name_exists(self, tag_name: str, group_id: int) -> bool:
        """
        Checks if a tag with the given name exists within a specific group.

        Args:
            tag_name (str): The name of the tag to check.
            group_id (int): The ID of the group to which the tag belongs.

        Returns:
            bool: True if the tag exists in the group, False otherwise.
        """

        cursor = self.db.cursor()
        cursor.execute("SELECT tag_id FROM tags WHERE tag_name = ? AND group_id = ?", (tag_name, group_id))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def tag_group_name_exists(self, group_name: str, project_id: int) -> bool:
        """
        Checks if a tag group with the given name exists within a specific project.
        
        Args:
            group_name (str): The name of the tag group to check.
            project_id (int): The ID of the project to which the tag group belongs.
        
        Returns:
            bool: True if the tag group exists in the project, False otherwise.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT group_id FROM tag_groups WHERE group_name = ? AND project_id = ?", (group_name, project_id))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def image_has_tag(self, image_id: int, tag_id: int) -> bool:
        """
        Checks if an image has been tagged with a specific tag.

        Args:
            image_id (int): The id of the image to check.
            tag_id (int): The id of the tag to check.

        Returns:
            bool: True if the image has the tag, False otherwise.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT tag_id FROM image_tags WHERE image_id = ? AND tag_id = ?", (image_id, tag_id))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def add_image_tag(self, image_id: int, tag_id: int):
        """
        Adds a tag to an image. If the image already has the tag, this does nothing.
        
        Args:
            image_id (int): The id of the image to add the tag to.
            tag_id (int): The id of the tag to add to the image.
        """

        cursor = self.db.cursor()
        cursor.execute("INSERT INTO image_tags (image_id, tag_id) VALUES (?, ?)", (image_id, tag_id))
        self.db.commit()
        cursor.close()

    def delete_image_tag(self, image_id: int, tag_id: int):
        """
        Deletes the specified tag from an image in the database.

        Args:
            image_id (int): The id of the image from which the tag will be removed.
            tag_id (int): The id of the tag to remove from the image.
        """

        cursor = self.db.cursor()
        cursor.execute("DELETE FROM image_tags WHERE image_id = ? AND tag_id = ?", (image_id, tag_id))
        self.db.commit()
        cursor.close()

    def get_image_tags(self, image_id: int) -> list[int]:
        """
        Gets a list of tag ids for the given image id.

        Args:
            image_id (int): The id of the image for which to retrieve tags.

        Returns:
            list[int]: A list of tag ids for the given image id.
        """
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
    
    def get_image_tag_count(self, image_id: int) -> int:
        """
        Gets the number of tags assigned to the given image id.

        Args:
            image_id (int): The id of the image for which to retrieve the tag count.

        Returns:
            int: The number of tags assigned to the given image id.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM image_tags WHERE image_id = ?", (image_id,))
        return cursor.fetchone()[0]
    
    def get_latest_unfinished_image_group(self, project_id: int) -> tuple[int, int, int] | None:
        """
        Retrieves the latest image group for a given project that has not met the minimum required tags.

        Args:
            project_id (int): The ID of the project to query.

        Returns:
            tuple[int, int, int] | None: A tuple containing the image ID, group ID, and display order of the latest
            unfinished image group, or None if all image groups are complete.

        The function performs the following:
        - It calculates the count of tags per image per group within the project.
        - Filters for required groups where the number of tags is less than the minimum required.
        - Orders the results to retrieve the latest image and the first incomplete group by display order.
        """

        cursor = self.db.cursor()
        cursor.execute(
            """
            WITH tagged_counts AS (
                -- Get the count of tags per image per group
                SELECT 
                    i.image_id,
                    i.project_id,
                    tg.group_id,
                    tg.display_order,
                    tg.min_tags,
                    tg.is_required,
                    COUNT(it.tag_id) as tag_count
                FROM images i
                CROSS JOIN tag_groups tg ON tg.project_id = i.project_id
                LEFT JOIN tags t ON t.group_id = tg.group_id
                LEFT JOIN image_tags it ON it.image_id = i.image_id AND it.tag_id = t.tag_id
                WHERE i.project_id = ?  -- Parameter for project_id
                GROUP BY i.image_id, tg.group_id
            )
            SELECT 
                tc.image_id,
                tc.group_id,
                tc.display_order
            FROM tagged_counts tc
            WHERE 
                tc.is_required = 1 
                AND tc.tag_count < tc.min_tags
            ORDER BY 
                tc.image_id DESC,  -- Get the latest image first
                tc.display_order ASC  -- Get the first incomplete group by display order
            LIMIT 1;
            """, (project_id,))
        result = cursor.fetchone()
        cursor.close()
        return result