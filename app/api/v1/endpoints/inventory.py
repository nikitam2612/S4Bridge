from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
)
from app.services.inventory_service import (
    create_inventory,
    get_all_inventory,
    get_inventory,
    get_inventory_by_product,
    update_inventory,
)

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory Management"],
)


@router.post(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory_endpoint(
    inventory_data: InventoryCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_inventory(db, inventory_data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[InventoryResponse],
)
def list_inventory_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_all_inventory(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/product/{product_id}",
    response_model=list[InventoryResponse],
)
def get_inventory_for_product_endpoint(
    product_id: int,
    warehouse_code: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_inventory_by_product(
        db,
        product_id,
        warehouse_code,
    )


@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def get_inventory_endpoint(
    inventory_id: int,
    db: Session = Depends(get_db),
):
    inventory = get_inventory(db, inventory_id)

    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found",
        )

    return inventory


@router.put(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def update_inventory_endpoint(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    db: Session = Depends(get_db),
):
    try:
        inventory = update_inventory(
            db,
            inventory_id,
            inventory_data,
        )

        if inventory is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory record not found",
            )

        return inventory

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
