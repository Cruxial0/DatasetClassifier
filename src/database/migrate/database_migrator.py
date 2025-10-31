import sqlite3
from datetime import datetime
import logging
from typing import List, Tuple, Optional, Union

class DatabaseMigration:
    def __init__(self, connection: Union[str, sqlite3.Connection]):
        """
        Initialize migration system with either a database path or an existing connection.
        
        Args:
            connection: Either a path to the database or an existing SQLite connection
        """
        self.connection = connection if isinstance(connection, sqlite3.Connection) else None
        self.db_path = connection if isinstance(connection, str) else None
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_connection(self) -> sqlite3.Connection:
        """Get the SQLite connection, creating one if needed."""
        if self.connection is not None:
            return self.connection
        return sqlite3.connect(self.db_path)

    def should_close_connection(self) -> bool:
        """Determine if we should close the connection after operations."""
        return self.connection is None

    def init_migration_table(self) -> None:
        """Create the migrations table if it doesn't exist."""
        conn = self.get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        if self.should_close_connection():
            conn.close()
            
    def get_current_version(self) -> int:
        """Get the latest applied migration version."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(version) FROM schema_migrations")
        result = cursor.fetchone()[0]
        if self.should_close_connection():
            conn.close()
        return result if result is not None else 0

    def is_migration_applied(self, version: int) -> bool:
        """Check if a specific migration version has already been applied."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM schema_migrations WHERE version = ?", (version,))
        result = cursor.fetchone()[0]
        if self.should_close_connection():
            conn.close()
        return result > 0

    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        if self.should_close_connection():
            conn.close()
        return column_name in columns

    def apply_migration(self, version: int, name: str, up_sql: str, down_sql: str) -> bool:
        """Apply a single migration."""
        conn = self.get_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        try:
            self.logger.info(f"Applying migration {version}: {name}")
            cursor.executescript(up_sql)
            
            cursor.execute(
                "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                (version, name)
            )

            if self.should_close_connection():
                conn.commit()
                conn.close()

            return True

        except sqlite3.Error as e:
            # Check if the error is about something that can be skipped
            if "already exists" in str(e).lower() or "duplicate column name" in str(e).lower():
                self.logger.warning(f"Migration {version} entities already exist: {str(e)}")
                
                # Insert the migration record if it doesn't exist
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO schema_migrations (version, name) VALUES (?, ?)",
                        (version, name)
                    )
                    if self.should_close_connection():
                        conn.commit()
                        conn.close()
                except sqlite3.Error as insert_error:
                    self.logger.error(f"Failed to record migration {version}: {str(insert_error)}")
                    if self.should_close_connection():
                        conn.rollback()
                        conn.close()
                    return False
                
                return True  # Return True because we're treating it as "applied"
            else:
                self.logger.error(f"Failed to apply migration {version}: {str(e)}")
                if self.should_close_connection():
                    conn.rollback()
                    conn.close()
                return False


    def rollback_migration(self, version: int, down_sql: str) -> bool:
        """Rollback a single migration."""
        try:
            conn = self.get_connection()
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            self.logger.info(f"Rolling back migration {version}")
            cursor.executescript(down_sql)
            
            cursor.execute(
                "DELETE FROM schema_migrations WHERE version = ?",
                (version,)
            )
            
            if self.should_close_connection():
                conn.commit()
                conn.close()
            
            return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to rollback migration {version}: {str(e)}")
            return False

    def migrate(self, migrations: List[Tuple[int, str, str, str]]) -> bool:
        """
        Apply all pending migrations up to target_version.
        migrations: List of tuples (version, name, up_sql, down_sql)
        """
        self.init_migration_table()
        current_version = self.get_current_version()
        target_version = max(m[0] for m in migrations)
            
        # Sort migrations by version
        migrations.sort(key=lambda x: x[0])
        
        if target_version > current_version:
            # Apply forward migrations
            for version, name, up_sql, down_sql in migrations:
                print(f"Checking migration {version}")
                
                # Skip if already applied
                if self.is_migration_applied(version):
                    print(f"Migration {version} already applied, skipping")
                    continue
                
                # Only apply if within range
                if current_version < version <= target_version:
                    if not self.apply_migration(version, name, up_sql, down_sql):
                        return False
                    print(f"Applied migration {version}")
                    
        elif target_version < current_version:
            # Apply rollback migrations
            for version, name, up_sql, down_sql in reversed(migrations):
                if target_version < version <= current_version:
                    if not self.rollback_migration(version, down_sql):
                        return False
                    
        return True