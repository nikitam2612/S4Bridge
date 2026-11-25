from sqlalchemy.orm import Session

from app.integrations.sync import sap_sync_service
from app.models.integration_event import IntegrationEvent
from app.schemas.integration import SAPSyncRequest


def test_duplicate_idempotency_key_returns_existing_event(
    test_engine,
    monkeypatch,
):
    from sqlalchemy.orm import sessionmaker

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
    )

    db: Session = TestingSessionLocal()

    calls = {"count": 0}

    def fake_store_payload(**kwargs):
        calls["count"] += 1

    def fake_update_response(**kwargs):
        pass

    class FakeSAPClient:
        def create_entity(self, entity_type, payload):
            return {
                "success": True,
                "external_id": "SAP-TEST-001",
            }

    monkeypatch.setattr(
        sap_sync_service,
        "store_integration_payload",
        fake_store_payload,
    )
    monkeypatch.setattr(
        sap_sync_service,
        "update_integration_response",
        fake_update_response,
    )
    monkeypatch.setattr(
        sap_sync_service,
        "sap_client",
        FakeSAPClient(),
    )

    request = SAPSyncRequest(
        entity_type="customer",
        operation="create",
        entity_id=1,
        idempotency_key="TEST-IDEMPOTENCY-001",
        payload={"company_name": "Test Company"},
    )

    try:
        first_event = sap_sync_service.sync_entity(db, request)
        second_event = sap_sync_service.sync_entity(db, request)

        event_count = (
            db.query(IntegrationEvent)
            .filter(IntegrationEvent.idempotency_key == "TEST-IDEMPOTENCY-001")
            .count()
        )

        assert first_event.event_id == second_event.event_id
        assert first_event.external_id == "SAP-TEST-001"
        assert second_event.status == "succeeded"
        assert event_count == 1
        assert calls["count"] == 1

    finally:
        db.close()


def test_sap_failure_marks_event_as_failed(
    test_engine,
    monkeypatch,
):
    from sqlalchemy.orm import sessionmaker

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
    )

    db = TestingSessionLocal()

    def fake_store_payload(**kwargs):
        pass

    class FailingSAPClient:
        def create_entity(self, entity_type, payload):
            raise RuntimeError("Simulated SAP connection failure")

    monkeypatch.setattr(
        sap_sync_service,
        "store_integration_payload",
        fake_store_payload,
    )
    monkeypatch.setattr(
        sap_sync_service,
        "sap_client",
        FailingSAPClient(),
    )

    request = SAPSyncRequest(
        entity_type="customer",
        operation="create",
        entity_id=1,
        idempotency_key="TEST-SAP-FAILURE-001",
        payload={"company_name": "Failure Test Company"},
    )

    try:
        import pytest

        with pytest.raises(
            RuntimeError,
            match="Simulated SAP connection failure",
        ):
            sap_sync_service.sync_entity(db, request)

        event = (
            db.query(IntegrationEvent)
            .filter_by(idempotency_key="TEST-SAP-FAILURE-001")
            .first()
        )

        assert event is not None
        assert event.status == "failed"
        assert "Simulated SAP connection failure" in event.error_message

    finally:
        db.close()
