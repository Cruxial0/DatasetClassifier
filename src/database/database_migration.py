import json
from pathlib import Path
from sqlite3 import Connection, Cursor

from src.project import Project
from src.database.database import DB_VERSION, Database

def get_base_directory(data: list[tuple[int, str, str, str, list[str], str]]) -> str:
    return Path(data[0][1]).parent.absolute().as_posix()

def create_project(db: Database, project_name: str, directories: list[str]) -> int:
    """
    Creates a new project in the database

    Returns:
        int: The project ID
    """

    return db.insert_project(project_name, directories)

def migrate(db: Database, project_name: str, data: list[tuple[int, str, str, str, list[str], str]]) -> Project:
    base_directory = get_base_directory(data)
    project_id = create_project(db, project_name, [base_directory])

    # Prepare data for batch insertion
    images_data = [(d[0], d[1], d[5], project_id) for d in data]
    scores_data = [(d[0], project_id, d[3], json.dumps(d[4]), d[5]) for d in data]
    
    cursor = db.connection.cursor()
    cursor.executemany("INSERT INTO images (image_id, source_path, timestamp, project_id) VALUES (?, ?, ?, ?)", 
                      images_data)
    cursor.executemany("INSERT INTO scores (image_id, project_id, score, categories, timestamp) VALUES (?, ?, ?, ?, ?)", 
                      scores_data)
    
    db.connection.commit()
    return Project(project_id, project_name, [base_directory], db)