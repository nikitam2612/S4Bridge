from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(
        min_length=2,
        max_length=100,
    )

    name: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    unit_price: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    unit_price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    external_id: str | None
    sku: str
    name: str
    description: str | None
    unit_price: Decimal
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
