from datetime import UTC, datetime
from typing import Any

from pymongo.errors import DuplicateKeyError

from app.db.mongodb import integration_payloads


def store_integration_payload(
    event_id: str,
    entity_type: str,
    entity_id: int,
    operation: str,
    request_payload: dict[str, Any],
) -> dict[str, Any]:

    document = {
        "event_id": event_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "operation": operation,
        "request_payload": request_payload,
        "response_payload": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    try:
        integration_payloads.insert_one(document)
    except DuplicateKeyError as exc:
        raise ValueError(
            "An integration payload already exists for this event"
        ) from exc

    return document


def update_integration_response(
    event_id: str,
    response_payload: dict[str, Any],
) -> bool:

    result = integration_payloads.update_one(
        {"event_id": event_id},
        {
            "$set": {
                "response_payload": response_payload,
                "updated_at": datetime.now(UTC),
            }
        },
    )

    return result.modified_count > 0


def get_integration_payload(
    event_id: str,
) -> dict[str, Any] | None:

    document = integration_payloads.find_one(
        {"event_id": event_id},
        {"_id": 0},
    )

    return document
