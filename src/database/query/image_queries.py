import json
from sqlite3 import Connection


class ImageQueries:
    def __init__(self, conn: Connection):
        self.conn = conn

    def add_or_update_score(self, source_path: str, score: str, categories: list[str]) -> None:
        # Get image info using source path
        cursor = self.conn.cursor()
        cursor.execute("SELECT image_id, project_id FROM images WHERE source_path = ?", (source_path,))
        result = cursor.fetchone()
        print("reached")
        if not result:
            raise ValueError(f"No image found with source path: {source_path}")
        
        print("reached")
        image_id, project_id = result
        categories_json = json.dumps(categories)

        # Update or insert score
        cursor.execute("""
            INSERT INTO scores (image_id, project_id, score, categories)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(image_id) 
            DO UPDATE SET score=?, categories=?, timestamp=CURRENT_TIMESTAMP
        """, (image_id, project_id, score, categories_json, score, categories_json))
        
        self.conn.commit()

    def is_image_scored(self, source_path: str) -> bool:
        # Get image id from source path, then check if it exists in scores table
        cursor = self.conn.connection.cursor()
        query = "SELECT id FROM images WHERE source_path = ?"
        cursor.execute(query, (source_path,))
        return cursor.fetchone() is not None
    
    def get_image_score(self, source_path: str) -> tuple[str | None, list[str]]:
        cursor = self.conn.cursor()
        query = """
        SELECT s.score, s.categories
        FROM images i
        JOIN scores s ON i.image_id = s.image_id
        WHERE i.source_path = ?;
        """

        result = cursor.execute(query, (source_path,)).fetchone()
        if result:
            return result[0], json.loads(result[1])
        return None, []
    
    def get_unique_categories(self, project_id: int) -> list[str]:
        cursor = self.conn.cursor()
        query = """
        SELECT categories
        FROM scores
        WHERE project_id = ?;
        """

        all_categories = cursor.execute(query, (project_id,)).fetchall()
        
        unique_categories = set()
        for categories_json in all_categories:
            categories = json.loads(categories_json[0])
            unique_categories.update(categories)
        
        return list(unique_categories)
    
    def get_project_scores(self, project_id: int) -> list[tuple[int, str, str, list[str]]]:
        """
        Gets all scores for a given project.

        Args:
            project_id (int): The id of the project to query.

        Returns:
            list[str]: A list of strings, each being the score of an image in the project.
        """
        cursor = self.conn.cursor()
        query = """
        SELECT s.image_id, i.source_path, s.score, s.categories
        FROM images i
        JOIN scores s ON i.image_id = s.image_id
        WHERE i.project_id = ?;
        """

        result = cursor.execute(query, (project_id,)).fetchall()
        return result
    
    def get_latest_image_id(self, project_id: int) -> int:
        cursor = self.conn.cursor()
        query = "SELECT MAX(image_id) FROM scores WHERE project_id = ?"
        image_id = cursor.execute(query, (project_id,)).fetchone()

        if image_id and image_id[0]:
            return image_id[0]
        return 0
    
    def add_images(self, source_paths: list[str], project_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.executemany("INSERT INTO images (source_path, project_id) VALUES (?, ?)", [(source_path, project_id) for source_path in source_paths])
        self.conn.commit()