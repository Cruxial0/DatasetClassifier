import json
import os
from src.database.database_legacy import LegacyDatabase
from src.utils import create_directory

class Project:
    def __init__(self, name, directories):
        self.name = name
        self.directories = directories
        self.db = get_or_create_database(name)

def create_project(project_name, directories) -> Project:
    pass

def get_or_create_database(project_name) -> LegacyDatabase:
    pass

def from_legacy_database(project_name) -> Project:
   """
    The legacy database consists of a single table with the following columns:
    (id, source_path, dest_path, score, categories, timestamp)
   """
   pass


def save_project(project: Project) -> None:
    """
    Save a project file that contains the project name and sqlite database path

    The save file is JSON encoded, saved with a .dcp (DatasetClassifier Project) extension
    """
    path = "./projects/{}.dcp".format(project.name)
    data = {'name': project.name, 'db_path': project.db.db_path}

    create_directory(os.path.dirname(path))

    with open(path, 'w') as f:
        f.write(json.dumps(data))