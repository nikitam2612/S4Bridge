from uuid import uuid4

from app.db.init_db import initialize_databases
from app.db.postgres import SessionLocal
from app.integrations.sync.sap_retry_service import (
    retry_failed_event,
)
from app.models.integration_event import IntegrationEvent
from app.services.integration_storage_service import (
    store_integration_payload,
)


def test_sap_retry():
    initialize_databases()

    db = SessionLocal()

    try:
        event_id = f"EVT-{uuid4().hex[:16].upper()}"

        # Create a test event in failed state
        event = IntegrationEvent(
            event_id=event_id,
            entity_type="customer",
            entity_id=999,
            operation="create",
            idempotency_key=f"retry-test-{uuid4().hex}",
            status="failed",
            error_message="Simulated temporary SAP failure",
            retry_count=0,
        )

        db.add(event)
        db.commit()

        # Store the original request payload in MongoDB
        store_integration_payload(
            event_id=event_id,
            entity_type="customer",
            entity_id=999,
            operation="create",
            request_payload={
                "company_name": "Retry Test Technologies",
                "contact_name": "Test User",
                "email": "retry-test@example.com",
            },
        )

        # Retry the failed event
        retried_event = retry_failed_event(
            db,
            event_id,
        )

        print("\n--- SAP Retry Test ---")
        print("Event ID:", retried_event.event_id)
        print("Event Status:", retried_event.status)
        print("Retry Count:", retried_event.retry_count)
        print("SAP External ID:", retried_event.external_id)

        assert retried_event.status == "succeeded"
        assert retried_event.retry_count == 1
        assert retried_event.external_id is not None

        print("\nSAP retry test passed!")

    finally:
        db.close()


if __name__ == "__main__":
    test_sap_retry()
