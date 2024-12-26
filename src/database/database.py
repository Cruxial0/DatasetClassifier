import json
import os
from pathlib import Path
import sqlite3
from src.database.query.tag_queries import TagQueries
from src.database.query.project_queries import ProjectQueries
from src.database.query.image_queries import ImageQueries
from src.database.queries import create_database

DB_VERSION = 1

class Database:
    def __init__(self, db_path="./db/dataset_classifier.db"):
        self.db_path = db_path
        self.connect()

        self.images = ImageQueries(self.connection)
        self.projects = ProjectQueries(self.connection)
        self.tags = TagQueries(self.connection)

    def connect(self):
        if os.path.exists(self.db_path):
            self.connection = sqlite3.connect(self.db_path)
            return
        
        path = Path(self.db_path)
        path.parent.mkdir(exist_ok=True)
        self.connection = sqlite3.connect(path.absolute().as_posix())
        self.connection.executescript(create_database())
        self.connection.commit()

    def insert_project(self, name: str, directories: list[str]) -> int:
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO projects (project_name, project_directories, version) VALUES (?, ?, ?);", (name, json.dumps(directories), DB_VERSION))
        cursor.connection.commit()
        
        return cursor.lastrowid

    def __del__(self):
        if self.connection:
            self.connection.close()