from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class SAPClient:
    def __init__(self):
        self.system_name = "S4Bridge-SAP-Simulator"
        self.system_version = "OData-Compatible-v1"

    def check_connection(self) -> dict[str, Any]:
        return {
            "connected": True,
            "system": self.system_name,
            "version": self.system_version,
            "checked_at": datetime.now(UTC).isoformat(),
        }

    def create_entity(
        self,
        entity_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "success": True,
            "operation": "create",
            "entity_type": entity_type,
            "external_id": f"SAP-{uuid4().hex[:12].upper()}",
            "message": (f"{entity_type} successfully created in simulated SAP"),
            "processed_at": datetime.now(UTC).isoformat(),
            "data": payload,
        }

    def update_entity(
        self,
        entity_type: str,
        external_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "success": True,
            "operation": "update",
            "entity_type": entity_type,
            "external_id": external_id,
            "message": (f"{entity_type} successfully updated in simulated SAP"),
            "processed_at": datetime.now(UTC).isoformat(),
            "data": payload,
        }


sap_client = SAPClient()
