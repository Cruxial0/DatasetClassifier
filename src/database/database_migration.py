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

def image_query(db: Database, image_id: int, source_path: str, timestamp: str, project_id: int):
    """
    Extracts the image data from the legacy database and inserts it into the new database
    """
    db.insert_image(image_id, source_path, project_id, timestamp)

def score_query(db: Database, image_id: int, project_id: int, score: str, categories: list[str], timestamp: str):
    """
    Extracts the score data from the legacy database and inserts it into the new database
    """

    db.insert_score(image_id, project_id, score, categories, timestamp)

def migrate(db: Database, project_name: str, data: list[tuple[int, str, str, str, list[str], str]]) -> Project:
    """
    Use a database connection to migrate from a legacy database to a new project-based database.
    A legacy database has these columns: (id, source_path, dest_path, score, categories, timestamp)

    The new database uses multiple tables for different categories.
    """
    base_directory = get_base_directory(data)
    project_id = create_project(db, project_name, [base_directory])

    # Iterate through the data and insert it into the new database (dest_path is deprecated)
    for image_id, source_path, _, score, categories, timestamp in data:
        image_query(db, image_id, source_path, timestamp, project_id)
        score_query(db, image_id, project_id, score, categories, timestamp)

    return Project(project_id, project_name, [base_directory], db)