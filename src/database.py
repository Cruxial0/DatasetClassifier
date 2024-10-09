from pathlib import Path
import sqlite3

class Database:
    def __init__(self, db_path='db/image_scores.db'):
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path.absolute().as_posix())
        self.cursor = self.conn.cursor()
        self.init_database()

    def init_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores
            (id INTEGER PRIMARY KEY,
             source_path TEXT,
             dest_path TEXT,
             score TEXT,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')
        self.conn.commit()

    def add_score(self, source_path, dest_path, score):
        self.cursor.execute('''
            INSERT INTO scores (source_path, dest_path, score)
            VALUES (?, ?, ?)
        ''', (source_path, dest_path, score))
        self.conn.commit()

    def remove_score(self, source_path, score):
        self.cursor.execute('''
            DELETE FROM scores
            WHERE source_path = ? AND score = ?
        ''', (source_path, score))
        self.conn.commit()

    def update_score(self, source_path, dest_path, score):
        self.cursor.execute('''
            SELECT dest_path FROM scores
            WHERE source_path = ? AND score = ?
        ''', (source_path, score))
        result = self.cursor.fetchone()
        
        if result:
            old_dest_path = result[0]
            self.cursor.execute('''
                UPDATE scores
                SET dest_path = ?, timestamp = CURRENT_TIMESTAMP
                WHERE source_path = ? AND score = ?
            ''', (dest_path, source_path, score))
        else:
            old_dest_path = None
            self.add_score(source_path, dest_path, score)
        
        self.conn.commit()
        return old_dest_path

    def get_image_scores(self, source_path):
        self.cursor.execute('''
            SELECT score FROM scores
            WHERE source_path = ?
        ''', (source_path,))
        return [row[0] for row in self.cursor.fetchall()]

    def is_image_scored(self, source_path):
        self.cursor.execute('''
            SELECT id FROM scores
            WHERE source_path = ?
            LIMIT 1
        ''', (source_path,))
        return self.cursor.fetchone() is not None

    def has_score(self, source_path, score):
        self.cursor.execute('''
            SELECT id FROM scores
            WHERE source_path = ? AND score = ?
            LIMIT 1
        ''', (source_path, score))
        return self.cursor.fetchone() is not None

    def close(self):
        self.conn.close()
