"""
Migration #4: Create categories and image_categories tables

This migration creates the new table structure.
Data migration is handled separately by migrate_category_data.py
"""

def create_categories_migration():
    """Returns SQL for creating category tables and indexes"""
    return """
-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    UNIQUE(project_id, category_name)
);

-- Create image_categories junction table
CREATE TABLE IF NOT EXISTS image_categories (
    image_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (image_id, category_id),
    FOREIGN KEY (image_id) REFERENCES images(image_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_categories_project ON categories(project_id);
CREATE INDEX IF NOT EXISTS idx_image_categories_image ON image_categories(image_id);
CREATE INDEX IF NOT EXISTS idx_image_categories_category ON image_categories(category_id);
"""

# For the migrations list
UP_SQL = create_categories_migration()
DOWN_SQL = """
DROP INDEX IF EXISTS idx_image_categories_category;
DROP INDEX IF EXISTS idx_image_categories_image;
DROP INDEX IF EXISTS idx_categories_project;
DROP TABLE IF EXISTS image_categories;
DROP TABLE IF EXISTS categories;
"""