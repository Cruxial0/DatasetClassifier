import json
from sqlite3 import Connection

class ProjectQueries:
    def __init__(self, db: Connection):
        self.db = db

    def load_project(self, project_id: int) -> tuple[int, str, list[str]]:
        cursor = self.db.cursor()
        query = "SELECT project_id, project_name, project_directories FROM projects WHERE project_id = ?"
        result = cursor.execute(query, (project_id,)).fetchone()

        if not result:
            raise ValueError(f"Project with id {project_id} not found")

        return (result[0], result[1], json.loads(result[2]))
    
    def load_projects_by_date(self) -> list[tuple[int, str, list[str]], str]:
        cursor = self.db.cursor()
        query = "SELECT project_id, project_name, project_directories, updated_at FROM projects ORDER BY updated_at DESC"
        result = cursor.execute(query).fetchall()

        return result
    
    def get_image_ids(self, project_id: int) -> list[int]:
        cursor = self.db.cursor()
        query = "SELECT image_id FROM images WHERE project_id = ?"
        result = cursor.execute(query, (project_id,)).fetchall()

        return [row[0] for row in result]
    
    def get_unscored_image_ids(self, project_id) -> list[int]:
        """Get unscored image IDs for a project"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT i.image_id 
            FROM images i
            LEFT JOIN scores s ON i.image_id = s.image_id
            WHERE i.project_id = ? AND s.score IS NULL
            ORDER BY i.image_id
        """, (project_id,))
        return [row[0] for row in cursor.fetchall()]