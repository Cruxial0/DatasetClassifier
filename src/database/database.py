from pathlib import Path
import sqlite3
from queries import create_database

class Database:
    def __init__(self, project_name, db_path=None):
        if project_name is None:
            raise ValueError("Project name is required")
        
        self.project_name = project_name
        self.connection = None

        if db_path is None:
            self.new()
        else:
            self.open(db_path)

    def new(self):
        path = Path("./projects") / f"{self.project_name}.db"
        path.parent.mkdir(exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.executescript(create_database())

    def open(self, db_path):
        self.connection = sqlite3.connect(db_path)

    def __del__(self):
        if self.connection:
            self.connection.close()