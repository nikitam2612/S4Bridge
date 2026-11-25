from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.integrations.sync.sap_retry_service import retry_failed_event
from app.integrations.sync.sap_sync_service import sync_entity
from app.models.integration_event import IntegrationEvent
from app.schemas.integration import (
    IntegrationEventResponse,
    SAPSyncRequest,
    SAPSyncResponse,
)

router = APIRouter(
    prefix="/integrations",
    tags=["SAP Integration"],
)


@router.post(
    "/sap/sync",
    response_model=SAPSyncResponse,
    status_code=status.HTTP_200_OK,
)
def synchronize_with_sap(
    sync_request: SAPSyncRequest,
    db: Session = Depends(get_db),
):
    try:
        event = sync_entity(db, sync_request)

        return SAPSyncResponse(
            event_id=event.event_id,
            entity_type=event.entity_type,
            operation=event.operation,
            status=event.status,
            external_id=event.external_id,
            message="SAP synchronization completed successfully",
            created_at=event.created_at,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SAP synchronization failed",
        ) from exc


@router.get(
    "/sap/events",
    response_model=list[IntegrationEventResponse],
)
def list_sap_integration_events(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    event_status: Literal["pending", "processing", "succeeded", "failed"]
    | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    query = select(IntegrationEvent)

    if event_status is not None:
        query = query.where(IntegrationEvent.status == event_status)

    query = query.order_by(IntegrationEvent.created_at.desc()).offset(skip).limit(limit)

    return list(db.scalars(query).all())


@router.get(
    "/sap/events/{event_id}",
    response_model=IntegrationEventResponse,
)
def get_sap_event_status(
    event_id: str,
    db: Session = Depends(get_db),
):
    event = db.scalar(
        select(IntegrationEvent).where(IntegrationEvent.event_id == event_id)
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration event not found",
        )

    return event


@router.post(
    "/sap/events/{event_id}/retry",
    response_model=SAPSyncResponse,
)
def retry_sap_synchronization(
    event_id: str,
    db: Session = Depends(get_db),
):
    try:
        event = retry_failed_event(db, event_id)

        return SAPSyncResponse(
            event_id=event.event_id,
            entity_type=event.entity_type,
            operation=event.operation,
            status=event.status,
            external_id=event.external_id,
            message="SAP synchronization retry completed successfully",
            created_at=event.created_at,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SAP retry failed",
        ) from exc
