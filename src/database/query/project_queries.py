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