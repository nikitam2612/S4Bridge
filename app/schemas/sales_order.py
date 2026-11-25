from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=10000)


class SalesOrderCreate(BaseModel):
    customer_id: int = Field(gt=0)

    warehouse_code: str = Field(
        default="MAIN",
        min_length=2,
        max_length=50,
    )

    items: list[OrderItemCreate] = Field(
        min_length=1,
    )


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class SalesOrderResponse(BaseModel):
    id: int
    order_number: str
    external_id: str | None
    customer_id: int
    warehouse_code: str
    status: str
    total_amount: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
