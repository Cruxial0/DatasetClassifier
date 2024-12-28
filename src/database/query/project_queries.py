import json
from sqlite3 import Connection

class ProjectQueries:
    def __init__(self, db: Connection):
        self.db = db

    def load(self, project_id: int) -> tuple[int, str, list[str]]:
        """
        Loads a project by ID from the database.

        Args:
            project_id (int): The ID of the project to load.

        Returns:
            tuple[int, str, list[str]]: A tuple containing the ID, name, and directories of the project.

        Raises:
            ValueError: If no project with the given ID is found.
        """

        cursor = self.db.cursor()
        query = "SELECT project_id, project_name, project_directories FROM projects WHERE project_id = ?"
        result = cursor.execute(query, (project_id,)).fetchone()

        if not result:
            raise ValueError(f"Project with id {project_id} not found")

        return (result[0], result[1], json.loads(result[2]))
    
    def load_projects_by_date(self) -> list[tuple[int, str, list[str]], str]:
        """
        Retrieve a list of all projects in the database, sorted by the last time they were modified.

        Returns:
            list[tuple[int, str, list[str]], str]: A list of tuples containing the project ID, project name, and project directories of all projects in the database, sorted by the last time they were modified (newest first). The last element of the tuple is the timestamp of the last modification, represented as a string in ISO 8601 format.
        """
        cursor = self.db.cursor()
        query = "SELECT project_id, project_name, project_directories, updated_at FROM projects ORDER BY updated_at DESC"
        result = cursor.execute(query).fetchall()

        return result
    
    def get_image_ids(self, project_id: int) -> list[int]:
        """
        Retrieve a list of image IDs for a given project.

        Args:
            project_id (int): The ID of the project for which to retrieve image IDs.

        Returns:
            list[int]: A list of image IDs associated with the provided project ID.
        """

        cursor = self.db.cursor()
        query = "SELECT image_id FROM images WHERE project_id = ?"
        result = cursor.execute(query, (project_id,)).fetchall()

        return [row[0] for row in result]
    
    def get_unscored_image_ids(self, project_id) -> list[int]:
        """
        Retrieve a list of image IDs for a given project that do not have a score associated with them.

        Args:
            project_id (int): The ID of the project for which to retrieve image IDs.

        Returns:
            list[int]: A list of image IDs associated with the provided project ID that do not have a score associated with them.
        """
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT i.image_id 
            FROM images i
            LEFT JOIN scores s ON i.image_id = s.image_id
            WHERE i.project_id = ? AND s.score IS NULL
            ORDER BY i.image_id
        """, (project_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def has_scores(self, project_id: int) -> bool:
        """Check if a project has any scored images
        
        Args:
            project_id (int): The ID of the project to check.
        
        Returns:
            bool: True if the project has scored images, False otherwise.
        
        Raises:
            ValueError: If the project ID is not found.
        """

        cursor = self.db.cursor()
        query = "SELECT COUNT(*) FROM scores WHERE project_id = ?"
        result = cursor.execute(query, (project_id,)).fetchone()

        if not result:
            raise ValueError(f"Project with id {project_id} not found")

        return result[0] > 0
    
    def has_tags(self, project_id: int) -> bool:
        """Check if a project has any tag groups

        Args:
            project_id (int): The ID of the project to check.

        Returns:
            bool: True if the project has tag groups, False otherwise.

        Raises:
            ValueError: If the project ID is not found.
        """
        
        cursor = self.db.cursor()
        query = "SELECT COUNT(*) FROM tag_groups WHERE project_id = ?"
        result = cursor.execute(query, (project_id,)).fetchone()

        if not result:
            raise ValueError(f"Project with id {project_id} not found")

        return result[0] > 0