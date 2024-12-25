from src.database.database import Database
from src.database.database_legacy import LegacyDatabase
from src.database.database_migration import migrate
from src.project import Project
from src.utils import get_image_paths, sanitize_string


def from_legacy_database(project_name: str, db_path: str, db: Database) -> Project:
   """
    The legacy database consists of a single table with the following columns:
    (id, source_path, dest_path, score, categories, timestamp)
   """
   legacy_db = LegacyDatabase(db_path)

   data = legacy_db.get_all_data()

   del legacy_db

   return migrate(db, project_name, data)


def new_project(project_name: str, directories: list[str], db: Database) -> Project:
    """
    Opens a new database connection, inserts a new project, then returns the project
    """
    project_name = sanitize_string(project_name)

    project_id = db.insert_project(project_name, directories)
    
    images = []
    for directory in directories:
        images.extend(get_image_paths(directory))

    db.images.add_images(images, project_id)

    return Project(project_id, project_name, directories, db)


def load_project_from_id(project_id: int, db: Database) -> Project:
    project = db.projects.load_project(project_id)

    return Project(project[0], project[1], project[2], db)