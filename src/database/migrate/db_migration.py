import src.database.migrate.migrations.create_database as init
from src.database.migrate.migrations import migration_001_categories

migrations = [
    (
        1,
        "Setup database schema",
        init.create_database(),
        None
    ),
    (
        2,
        "Add condition column",
        "ALTER TABLE tag_groups ADD COLUMN condition TEXT;",
        None
    ),
    (
        3,
        "Add tag rules table",
        """CREATE TABLE IF NOT EXISTS export_tag_rules (
            rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            rule_name TEXT NOT NULL,
            condition TEXT NOT NULL,
            tags_to_add TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
        )""",
        None
    ),
    (
        4,
        "Refactor categories to dedicated tables",
        migration_001_categories.create_categories_migration(),
        None
    )
]