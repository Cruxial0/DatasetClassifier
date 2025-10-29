import src.database.migrate.migrations.create_database as init

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
    )
]