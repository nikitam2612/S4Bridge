from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SAPSyncRequest(BaseModel):
    entity_type: Literal[
        "customer",
        "product",
        "sales_order",
        "inventory",
    ]

    operation: Literal["create", "update"]

    entity_id: int = Field(gt=0)

    idempotency_key: str = Field(
        min_length=8,
        max_length=150,
    )

    payload: dict[str, Any] = Field(min_length=1)


class SAPSyncResponse(BaseModel):
    event_id: str
    entity_type: str
    operation: str

    status: Literal[
        "pending",
        "processing",
        "succeeded",
        "failed",
    ]

    external_id: str | None = None
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntegrationEventResponse(BaseModel):
    event_id: str
    entity_type: str
    entity_id: int
    operation: str

    status: Literal[
        "pending",
        "processing",
        "succeeded",
        "failed",
    ]

    external_id: str | None = None
    error_message: str | None = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
