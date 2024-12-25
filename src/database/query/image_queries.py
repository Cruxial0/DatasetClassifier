import json
from database.database import Database


class ImageQueries:
    def __init__(self, db: Database):
        self.db = db

    def add_or_update_score(self, source_path: str, score: str, categories: list[str]):
        # Get image info using source path
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT i.image_id, i.project_id 
            FROM images i 
            WHERE i.source_path = ?
        """, (source_path,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError(f"No image found with source path: {source_path}")
            
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
        query = "SELECT id FROM images WHERE source_path = ?"
        self.db.cursor.execute(query, (source_path,))
        return self.db.cursor.fetchone() is not None
    
    def get_image_score(self, source_path: str) -> tuple[str | None, list[str]]:
        query = """
        SELECT s.score s.categories
        FROM images i
        JOIN scores s ON i.id = s.image_id
        WHERE i.source_path = ?;
        """

        result = self.db.cursor.execute(query, (source_path,)).fetchone()
        if result:
            return result[0], json.loads(result[1])
        return None, []
