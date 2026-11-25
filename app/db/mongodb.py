from pymongo import ASCENDING, DESCENDING, MongoClient

from app.core.config import settings

mongo_client = MongoClient(
    settings.MONGODB_URL,
    serverSelectionTimeoutMS=5000,
)

mongo_database = mongo_client[settings.MONGODB_DATABASE]

integration_payloads = mongo_database["integration_payloads"]


def check_mongodb_connection():
    try:
        mongo_client.admin.command("ping")
        return True
    except Exception:
        return False


def initialize_mongodb_indexes():
    integration_payloads.create_index(
        [("event_id", ASCENDING)],
        unique=True,
    )

    integration_payloads.create_index(
        [("entity_type", ASCENDING)],
    )

    integration_payloads.create_index(
        [("created_at", DESCENDING)],
    )
