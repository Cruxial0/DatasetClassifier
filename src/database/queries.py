def create_projects_schema():
    return """
    CREATE TABLE projects(
        project_id INTEGER PRIMARY KEY,
        project_name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        version INTEGER DEFAULT 1
    );"""

def create_scores_schema():
    return """
    CREATE TABLE scores(
        image_id INTEGER PRIMARY KEY,
        project_id INTEGER NOT NULL,
        source_path TEXT NOT NULL,
        score INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
    );"""

def create_tag_groups_schema():
    return """
    CREATE TABLE tag_groups (
        group_id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        group_name TEXT NOT NULL,
        is_required BOOLEAN NOT NULL DEFAULT 0,
        allow_multiple BOOLEAN NOT NULL DEFAULT 0,
        min_tags INTEGER DEFAULT 0,
        display_order INTEGER DEFAULT 0,
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
    );"""

def create_tags_schema():
    return """
    CREATE TABLE tags (
        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        tag_name TEXT NOT NULL,
        display_order INTEGER NOT NULL,
        FOREIGN KEY (group_id) REFERENCES tag_groups(group_id)
    );"""

def create_image_tags_schema():
    return """
    CREATE TABLE image_tags (
        image_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (image_id, tag_id),
        FOREIGN KEY (image_id) REFERENCES images(image_id),
        FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
    );"""

def create_indexes():
    return """
    CREATE INDEX idx_images_project ON images(project_id);
    CREATE INDEX idx_tag_groups_project ON tag_groups(project_id);
    CREATE INDEX idx_tags_group ON tags(group_id);
    CREATE INDEX idx_image_tags_image ON image_tags(image_id);
    """

def create_database():
    return f"""
    PRAGMA foreign_keys = ON;
    {create_projects_schema()}
    {create_scores_schema()}
    {create_tag_groups_schema()}
    {create_tags_schema()}
    {create_image_tags_schema()}
    {create_indexes()}
    """