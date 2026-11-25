from uuid import uuid4

from app.db.init_db import initialize_databases
from app.db.postgres import SessionLocal
from app.integrations.sync.sap_sync_service import sync_entity
from app.schemas.integration import SAPSyncRequest
from app.services.integration_storage_service import (
    get_integration_payload,
)


def test_sap_sync():
    initialize_databases()

    db = SessionLocal()

    try:
        request = SAPSyncRequest(
            entity_type="customer",
            operation="create",
            entity_id=1,
            idempotency_key=f"test-customer-{uuid4().hex}",
            payload={
                "company_name": "Acme Technologies",
                "contact_name": "Rahul Sharma",
                "email": "rahul@acme.com",
            },
        )

        event = sync_entity(db, request)

        payload = get_integration_payload(event.event_id)

        print("\n--- SAP Synchronization Test ---")
        print("Event ID:", event.event_id)
        print("Event Status:", event.status)
        print("SAP External ID:", event.external_id)
        print("MongoDB Payload Found:", payload is not None)

        if payload:
            print(
                "SAP Response Success:",
                payload["response_payload"]["success"],
            )

        assert event.status == "succeeded"
        assert event.external_id is not None
        assert payload is not None
        assert payload["response_payload"]["success"] is True

        print("\nSAP synchronization test passed!")

    finally:
        db.close()


if __name__ == "__main__":
    test_sap_sync()
