from src.database.database import Database

class Project:
    def __init__(self, id: int, name: str, directories: list[str], database: Database):
        self.id = id
        self.name = name
        self.directories = directories
        self.db = database