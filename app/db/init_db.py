from app.db.mongodb import (
    initialize_mongodb_indexes,
    mongo_client,
)
from app.db.postgres import engine


def initialize_databases():
    # Verify PostgreSQL connection
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    # Verify MongoDB connection
    mongo_client.admin.command("ping")

    # Initialize MongoDB indexes
    initialize_mongodb_indexes()


def close_databases():
    engine.dispose()
    mongo_client.close()
