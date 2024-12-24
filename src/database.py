import json
from pathlib import Path
import sqlite3
from typing import List

from src.export import Image

class Database:
    def __init__(self, db_path='db/image_scores.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path.absolute().as_posix())
        self.cursor = self.conn.cursor()
        self.init_database()

    def init_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores
            (id INTEGER PRIMARY KEY,
             source_path TEXT,
             dest_path TEXT,
             score TEXT,
             categories TEXT,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
             UNIQUE(source_path, dest_path))
        ''')
        self.conn.commit()

    def wipe_database(self):
        self.cursor.execute('DELETE FROM scores')
        self.conn.commit()

    def rebuild_from_filesystem(self, input_directory, output_directory):
        # self.wipe_database()
        input_path = Path(input_directory)
        output_path = Path(output_directory)
        
        for score_folder in output_path.iterdir():
            if score_folder.is_dir() and score_folder.name in ['score_9', 'score_8_up', 'score_7_up', 'score_6_up', 'score_5_up', 'score_4_up', 'discard']:
                score = score_folder.name
                
                # Step 1: Insert all images in the score folder into the database
                for image_path in score_folder.glob('*'):
                    if image_path.is_file() and image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                        relative_path = image_path.relative_to(output_path)
                        source_path = str(input_path / image_path.name).replace('/', '\\')
                        dest_path = str(image_path).replace('/', '\\')
                        self.add_or_update_score(source_path, dest_path, score, [])

                # Step 2: Process subfolders for categories
                for subfolder in score_folder.iterdir():
                    if subfolder.is_dir():
                        category = subfolder.name
                        for image_path in subfolder.glob('*'):
                            if image_path.is_file() and image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                                source_path = str(input_path / image_path.name).replace('/', '\\')
                                dest_path = str(image_path).replace('/', '\\')
                                
                                # Check if entry exists and update categories
                                self.cursor.execute('''
                                    SELECT categories FROM scores
                                    WHERE source_path = ?
                                ''', (source_path,))
                                result = self.cursor.fetchone()
                                if result:
                                    categories = json.loads(result[0])
                                    if category not in categories:
                                        categories.append(category)
                                    self.update_categories(source_path, categories)
                                else:
                                    # If entry doesn't exist, add it with the category
                                    self.add_or_update_score(source_path, dest_path, score, [category])

        self.conn.commit()

    def add_or_update_score(self, source_path, dest_path, score, categories):
        categories_json = json.dumps(categories)
        source_path = source_path.replace('/', '\\') if source_path else None
        dest_path = dest_path.replace('/', '\\') if dest_path else None
        
        # Check if a row with the current source_path exists
        self.cursor.execute('SELECT COUNT(1) FROM scores WHERE source_path = ?', (source_path,))
        row_exists = self.cursor.fetchone()[0]
        
        if row_exists:
            # If it exists, update the score
            self.cursor.execute('''
                UPDATE scores
                SET score = ?, categories = ?, dest_path = ?
                WHERE source_path = ?
            ''', (score, categories_json, dest_path, source_path))
        else:
            # If it doesn't exist, insert a new row
            self.cursor.execute('''
                INSERT INTO scores (source_path, dest_path, score, categories)
                VALUES (?, ?, ?, ?)
            ''', (source_path, dest_path, score, categories_json))
        
        self.conn.commit()



    def update_categories(self, source_path, categories):
        categories_json = json.dumps(categories)
        self.cursor.execute('''
            UPDATE scores
            SET categories = ?, timestamp = CURRENT_TIMESTAMP
            WHERE source_path = ?
        ''', (categories_json, source_path.replace('/', '\\')))
        self.conn.commit()

    def get_image_score(self, source_path):
        self.cursor.execute('''
            SELECT score, categories FROM scores
            WHERE source_path = ?
        ''', (source_path.replace('/', '\\'),))
        result = self.cursor.fetchone()
        if result:
            return result[0], json.loads(result[1])
        return None, []

    def is_image_scored(self, source_path):
        self.cursor.execute('''
            SELECT id FROM scores
            WHERE source_path = ?
            LIMIT 1
        ''', (source_path.replace('/', '\\'),))
        return self.cursor.fetchone() is not None

    def get_all_scores(self):
        self.cursor.execute('SELECT source_path, dest_path, score, categories FROM scores')
        return [(row[0].replace('/', '\\'), row[1].replace('/', '\\'), row[2], json.loads(row[3])) for row in self.cursor.fetchall()]
    
    def get_unique_categories(self):
        self.cursor.execute('SELECT categories FROM scores')
        all_categories = self.cursor.fetchall()
        
        unique_categories = set()
        for categories_json in all_categories:
            categories = json.loads(categories_json[0])
            unique_categories.update(categories)
        
        return list(unique_categories)
    
    def get_all_images(self) -> List[Image]:
        self.cursor.execute('SELECT id, source_path, dest_path, score, categories FROM scores')
        rows = self.cursor.fetchall()

        images = []
        for row in rows:
            image_id, source_path, dest_path, score, categories_json = row
            categories = json.loads(categories_json)
            images.append(Image(
                id=image_id,
                source_path=source_path.replace('/', '\\'),
                dest_path=dest_path.replace('/', '\\'),
                score=str(score),
                categories=categories
            ))
        
        return images
    
    def get_latest_image_id(self):
        self.cursor.execute('SELECT id FROM scores ORDER BY timestamp DESC LIMIT 1')
        return self.cursor.fetchone()[0]

    def write_sidecar(self):
        data = [
            {
                'source_path': row[0].replace('/', '\\'),
                'dest_path': row[1].replace('/', '\\'),
                'score': row[2],
                'categories': row[3]
            }
            for row in self.get_all_scores()
        ]
        with open(self.sidecar_path, 'w') as f:
            json.dump(data, f)

    def close(self):
        self.conn.close()
