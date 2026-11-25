from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.integrations.sap.sap_client import sap_client
from app.models.integration_event import IntegrationEvent
from app.schemas.integration import SAPSyncRequest
from app.services.integration_storage_service import (
    store_integration_payload,
    update_integration_response,
)


def sync_entity(
    db: Session,
    sync_request: SAPSyncRequest,
) -> IntegrationEvent:

    # 1. Check whether this idempotency key already exists
    existing_event = db.scalar(
        select(IntegrationEvent).where(
            IntegrationEvent.idempotency_key == sync_request.idempotency_key
        )
    )

    if existing_event:
        return existing_event

    # 2. Create a new integration event
    event_id = f"EVT-{uuid4().hex[:16].upper()}"

    event = IntegrationEvent(
        event_id=event_id,
        entity_type=sync_request.entity_type,
        entity_id=sync_request.entity_id,
        operation=sync_request.operation,
        idempotency_key=sync_request.idempotency_key,
        status="pending",
    )

    db.add(event)

    try:
        # The database unique constraint protects concurrent requests
        db.commit()

    except IntegrityError:
        db.rollback()

        # Another request may have inserted the same idempotency key
        existing_event = db.scalar(
            select(IntegrationEvent).where(
                IntegrationEvent.idempotency_key == sync_request.idempotency_key
            )
        )

        if existing_event is not None:
            return existing_event

        # The integrity error was caused by something else
        raise

    db.refresh(event)

    # Preserve the event's database ID for failure handling
    event_db_id = event.id

    try:
        # 3. Store the outgoing request in MongoDB
        store_integration_payload(
            event_id=event_id,
            entity_type=sync_request.entity_type,
            entity_id=sync_request.entity_id,
            operation=sync_request.operation,
            request_payload=sync_request.payload,
        )

        # 4. Mark the event as processing
        event.status = "processing"
        db.commit()

        # 5. Send the request to simulated SAP
        if sync_request.operation == "create":
            response = sap_client.create_entity(
                entity_type=sync_request.entity_type,
                payload=sync_request.payload,
            )

        else:
            external_id = sync_request.payload.get("external_id")

            if not external_id:
                raise ValueError("external_id is required for SAP update operations")

            response = sap_client.update_entity(
                entity_type=sync_request.entity_type,
                external_id=external_id,
                payload=sync_request.payload,
            )

        # 6. Store the SAP response in MongoDB
        update_integration_response(
            event_id=event_id,
            response_payload=response,
        )

        # 7. Update the PostgreSQL event status
        event.status = "succeeded"
        event.external_id = response["external_id"]
        event.error_message = None

        db.commit()
        db.refresh(event)

        return event

    except Exception as exc:
        db.rollback()

        # Record the failure for monitoring and future retries
        failed_event = db.get(
            IntegrationEvent,
            event_db_id,
        )

        if failed_event is not None:
            failed_event.status = "failed"
            failed_event.error_message = str(exc)
            db.commit()
            db.refresh(failed_event)

        raise
