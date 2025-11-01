import json
from sqlite3 import Connection

from src.export_image import ExportImage


class ImageQueries:
    def __init__(self, conn: Connection):
        self.conn = conn

    def add_or_update_score(self, source_path: str, score: str, categories: list[str]) -> bool:
        """
        Add or update a score and categories for an image.
        
        Args:
            source_path: Path to the image file
            score: Score value to assign
            categories: List of categories to assign
            
        Returns:
            bool: True if the score was successfully added/updated, False otherwise
            
        Raises:
            ValueError: If no image is found with the given source path
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT image_id, project_id FROM images WHERE source_path = ?", (source_path,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError(f"No image found with source path: {source_path}")
            
            image_id, project_id = result
            categories_json = json.dumps(categories)

            cursor.execute("""
                INSERT INTO scores (image_id, project_id, score, categories)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(image_id) 
                DO UPDATE SET score=?, categories=?, timestamp=CURRENT_TIMESTAMP
            """, (image_id, project_id, score, categories_json, score, categories_json))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating score: {e}")
            return False

    def get_path(self, image_id: int) -> str:
        cursor = self.conn.cursor()
        query = "SELECT source_path FROM images WHERE image_id = ? LIMIT 1"
        return cursor.execute(query, (image_id,)).fetchone()[0]

    def is_scored(self, source_path: str) -> bool:
        # Get image id from source path, then check if it exists in scores table
        cursor = self.conn.connection.cursor()
        query = "SELECT id FROM images WHERE source_path = ?"
        cursor.execute(query, (source_path,))
        return cursor.fetchone() is not None
    
    def get_score(self, source_path: str) -> tuple[str | None, list[str]]:
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
    
    def add(self, source_paths: list[str], project_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.executemany("INSERT INTO images (source_path, project_id) VALUES (?, ?)", [(source_path, project_id) for source_path in source_paths])
        self.conn.commit()

    def get_export_images(self, project_id: int) -> list[ExportImage]:
        """
        Get all images for export with their scores, categories, and tag IDs.
        
        Args:
            project_id: The project ID to get images from
            
        Returns:
            List of ExportImage objects with tag_ids populated
        """
        cursor = self.conn.cursor()

        # Get all images with their data in one query
        images_query = """
        SELECT images.image_id, images.source_path, scores.score, scores.categories
        FROM images
        LEFT JOIN scores ON images.image_id = scores.image_id
        WHERE images.project_id = ?
        ORDER BY images.image_id
        """
        
        cursor.execute(images_query, (project_id,))
        image_data = cursor.fetchall()
        
        # Get all tag IDs for all images in the project in one query
        tags_query = """
        SELECT it.image_id, it.tag_id
        FROM image_tags it
        INNER JOIN images i ON it.image_id = i.image_id
        WHERE i.project_id = ?
        ORDER BY it.image_id, it.tag_id
        """
        
        cursor.execute(tags_query, (project_id,))
        tag_data = cursor.fetchall()
        
        # Group tags by image_id
        tags_by_image = {}
        for image_id, tag_id in tag_data:
            if image_id not in tags_by_image:
                tags_by_image[image_id] = []
            tags_by_image[image_id].append(tag_id)
        
        # Build ExportImage objects
        output = []
        for image_id, source_path, score, categories in image_data:
            # Parse categories
            categories = [] if categories is None else json.loads(categories)
            
            # Get tag IDs for this image (empty list if none)
            tag_ids = tags_by_image.get(image_id, [])
            
            # Create ExportImage with all required fields
            output.append(ExportImage(
                id=image_id,
                source_path=source_path,
                dest_path=None,
                score=score,
                categories=categories,
                tag_ids=tag_ids,
                additional_tags=None
            ))
        
        cursor.close()
        return output