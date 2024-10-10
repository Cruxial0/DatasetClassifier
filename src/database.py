import json
from pathlib import Path
import sqlite3

class Database:
    def __init__(self, db_path='db/image_scores.db', sidecar_path='db/sidecar.json'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path.absolute().as_posix())
        self.cursor = self.conn.cursor()
        self.sidecar_path = Path(sidecar_path)
        self.init_database()

    def init_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores
            (id INTEGER PRIMARY KEY,
             source_path TEXT UNIQUE,
             dest_path TEXT,
             score TEXT,
             categories TEXT,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')
        self.conn.commit()

    def wipe_database(self):
        self.cursor.execute('DELETE FROM scores')
        self.conn.commit()

    def rebuild_from_sidecar(self):
        return False # Temporary, might change later
        if self.sidecar_path.exists():
            with open(self.sidecar_path, 'r') as f:
                data = json.load(f)
            self.wipe_database()
            for entry in data:
                self.add_or_update_score(entry['source_path'], entry['dest_path'], entry['score'], entry['categories'])
            return True
        return False

    def rebuild_from_filesystem(self, input_directory, output_directory):
        self.wipe_database()
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
        self.cursor.execute('''
            INSERT OR REPLACE INTO scores (source_path, dest_path, score, categories)
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

    def remove_score(self, source_path):
        self.cursor.execute('''
            DELETE FROM scores
            WHERE source_path = ?
        ''', (source_path.replace('/', '\\'),))
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
