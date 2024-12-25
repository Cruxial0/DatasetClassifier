from src.database.database import Database
from src.database.database_legacy import LegacyDatabase
from src.database.database_migration import migrate
from src.project import Project
from src.utils import sanitize_string


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

    return Project(project_id, project_name, directories, db)