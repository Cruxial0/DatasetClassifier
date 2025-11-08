from sqlite3 import Connection
from typing import List, Tuple


class CategoryQueries:
    """Database queries for managing categories"""
    
    def __init__(self, db: Connection):
        self.db = db
    
    def get_project_categories(self, project_id: int) -> List[Tuple[int, str, int]]:
        """
        Get all categories for a project
        
        Args:
            project_id: The project ID
            
        Returns:
            List of tuples: (category_id, category_name, display_order)
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT category_id, category_name, display_order
            FROM categories
            WHERE project_id = ?
            ORDER BY display_order
        """, (project_id,))
        
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def add_category(self, project_id: int, category_name: str, display_order: int) -> int:
        """
        Add a new category to a project
        
        Args:
            project_id: The project ID
            category_name: Name of the category
            display_order: Display order for the category
            
        Returns:
            The ID of the newly created category
        """
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO categories (project_id, category_name, display_order)
                VALUES (?, ?, ?)
            """, (project_id, category_name, display_order))
            
            self.db.commit()
            category_id = cursor.lastrowid
            cursor.close()
            return category_id
            
        except Exception as e:
            print(f"Error adding category: {e}")
            cursor.close()
            raise
    
    def delete_category(self, category_id: int):
        """
        Delete a category
        
        Args:
            category_id: The category ID to delete
        """
        cursor = self.db.cursor()
        
        # Delete will cascade to image_categories due to foreign key
        cursor.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
        
        self.db.commit()
        cursor.close()
    
    def update_category_order(self, new_order: List[Tuple[int, int]]):
        """
        Update the display order of categories
        
        Args:
            new_order: List of tuples (category_id, new_display_order)
        """
        cursor = self.db.cursor()
        cursor.executemany(
            "UPDATE categories SET display_order = ? WHERE category_id = ?",
            [(order[1], order[0]) for order in new_order]
        )
        self.db.commit()
        cursor.close()
    
    def category_exists(self, project_id: int, category_name: str) -> bool:
        """
        Check if a category with the given name exists in the project
        
        Args:
            project_id: The project ID
            category_name: Name to check
            
        Returns:
            True if exists, False otherwise
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT category_id FROM categories
            WHERE project_id = ? AND category_name = ?
        """, (project_id, category_name))
        
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def get_category_id(self, project_id: int, category_name: str) -> int:
        """
        Get the ID of a category by name
        
        Args:
            project_id: The project ID
            category_name: Name of the category
            
        Returns:
            Category ID or None if not found
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT category_id FROM categories
            WHERE project_id = ? AND category_name = ?
        """, (project_id, category_name))
        
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    
    def get_image_categories(self, image_id: int) -> List[int]:
        """
        Get all category IDs for an image
        
        Args:
            image_id: The image ID
            
        Returns:
            List of category IDs
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT category_id FROM image_categories
            WHERE image_id = ?
        """, (image_id,))
        
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
    
    def get_image_category_names(self, image_id: int) -> List[str]:
        """
        Get all category names for an image
        
        Args:
            image_id: The image ID
            
        Returns:
            List of category names
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT c.category_name
            FROM image_categories ic
            JOIN categories c ON ic.category_id = c.category_id
            WHERE ic.image_id = ?
            ORDER BY c.display_order
        """, (image_id,))
        
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
    
    def add_image_category(self, image_id: int, category_id: int):
        """
        Add a category to an image
        
        Args:
            image_id: The image ID
            category_id: The category ID
        """
        cursor = self.db.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO image_categories (image_id, category_id)
                VALUES (?, ?)
            """, (image_id, category_id))
            
            self.db.commit()
        except Exception as e:
            # Ignore duplicate key errors (category already assigned)
            if "UNIQUE constraint failed" not in str(e):
                print(f"Error adding image category: {e}")
        
        cursor.close()
    
    def remove_image_category(self, image_id: int, category_id: int):
        """
        Remove a category from an image
        
        Args:
            image_id: The image ID
            category_id: The category ID
        """
        cursor = self.db.cursor()
        cursor.execute("""
            DELETE FROM image_categories
            WHERE image_id = ? AND category_id = ?
        """, (image_id, category_id))
        
        self.db.commit()
        cursor.close()
    
    def image_has_category(self, image_id: int, category_id: int) -> bool:
        """
        Check if an image has a specific category
        
        Args:
            image_id: The image ID
            category_id: The category ID
            
        Returns:
            True if the image has the category, False otherwise
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 1 FROM image_categories
            WHERE image_id = ? AND category_id = ?
        """, (image_id, category_id))
        
        result = cursor.fetchone()
        cursor.close()
        return result is not None