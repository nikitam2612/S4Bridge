from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderResponse,
)
from app.services.sales_order_service import (
    create_sales_order,
    get_sales_order,
    get_sales_orders,
)

router = APIRouter(
    prefix="/sales-orders",
    tags=["Sales Order Management"],
)


@router.post(
    "",
    response_model=SalesOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sales_order_endpoint(
    order_data: SalesOrderCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_sales_order(db, order_data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[SalesOrderResponse],
)
def list_sales_orders_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_sales_orders(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{order_id}",
    response_model=SalesOrderResponse,
)
def get_sales_order_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = get_sales_order(db, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found",
        )

    return order
