import src.database.migrate.migrations.create_database as init

migrations = [
    (
        1,
        "Setup database schema",
        init.create_database(),
        None
    )
]