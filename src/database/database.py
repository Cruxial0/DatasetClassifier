import json
import os
from pathlib import Path
import sqlite3
from src.database.query.image_queries import ImageQueries
from src.database.queries import create_database

DB_VERSION = 1

class Database:
    def __init__(self, db_path="./db/dataset_classifier.db"):
        self.db_path = db_path
        self.image = ImageQueries(self)
        self.connect()

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
    
    def insert_image(self, image_id: int, source_path: str, project_id: int, timestamp: str = None) -> None:
        cursor = self.connection.cursor()
        if timestamp is None:
            cursor.execute("INSERT INTO images (image_id, source_path, project_id) VALUES (?, ?, ?);", (image_id, source_path, project_id))
        else:
            cursor.execute("INSERT INTO images (image_id, source_path, timestamp, project_id) VALUES (?, ?, ?, ?);", (image_id, source_path, timestamp, project_id))
        cursor.connection.commit()

    def insert_score(self, image_id: int, project_id: int, score: str, categories: list[str], timestamp: str = None) -> None:
        cursor = self.connection.cursor()
        if timestamp is None:
            cursor.execute("INSERT INTO scores (image_id, project_id, score, categories) VALUES (?, ?, ?, ?);", (image_id, project_id, score, json.dumps(categories)))
        else:
            cursor.execute("INSERT INTO scores (image_id, project_id, score, categories, timestamp) VALUES (?, ?, ?, ?, ?);", (image_id, project_id, score, json.dumps(categories), timestamp))
        cursor.connection.commit()

    def __del__(self):
        if self.connection:
            self.connection.close()