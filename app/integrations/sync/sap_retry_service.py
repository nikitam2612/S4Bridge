from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.sap.sap_client import sap_client
from app.models.integration_event import IntegrationEvent
from app.services.integration_storage_service import (
    get_integration_payload,
    update_integration_response,
)

MAX_RETRIES = 3


def retry_failed_event(
    db: Session,
    event_id: str,
) -> IntegrationEvent:

    event = db.scalar(
        select(IntegrationEvent).where(IntegrationEvent.event_id == event_id)
    )

    if event is None:
        raise ValueError("Integration event not found")

    if event.status == "succeeded":
        raise ValueError("Successful events cannot be retried")

    if event.status not in ("failed", "pending"):
        raise ValueError(f"Event cannot be retried from status: {event.status}")

    if event.retry_count >= MAX_RETRIES:
        raise ValueError("Maximum retry attempts exceeded")

    payload_document = get_integration_payload(event_id)

    if payload_document is None:
        raise ValueError("Original integration payload not found")

    request_payload = payload_document["request_payload"]

    event.status = "processing"
    event.retry_count += 1
    event.error_message = None
    db.commit()

    try:
        if event.operation == "create":
            response = sap_client.create_entity(
                entity_type=event.entity_type,
                payload=request_payload,
            )

        elif event.operation == "update":
            external_id = request_payload.get("external_id")

            if not external_id:
                raise ValueError("external_id is required for update operations")

            response = sap_client.update_entity(
                entity_type=event.entity_type,
                external_id=external_id,
                payload=request_payload,
            )

        else:
            raise ValueError("Unsupported integration operation")

        update_integration_response(
            event_id=event_id,
            response_payload=response,
        )

        event.status = "succeeded"
        event.external_id = response["external_id"]
        event.error_message = None

        db.commit()
        db.refresh(event)

        return event

    except Exception as exc:
        db.rollback()

        event = db.scalar(
            select(IntegrationEvent).where(IntegrationEvent.event_id == event_id)
        )

        event.status = "failed"
        event.error_message = str(exc)

        db.commit()
        db.refresh(event)

        raise
