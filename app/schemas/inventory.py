from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InventoryCreate(BaseModel):
    product_id: int = Field(gt=0)

    warehouse_code: str = Field(
        min_length=2,
        max_length=50,
    )

    quantity_on_hand: int = Field(
        default=0,
        ge=0,
    )

    quantity_reserved: int = Field(
        default=0,
        ge=0,
    )

    reorder_level: int = Field(
        default=10,
        ge=0,
    )

    @model_validator(mode="after")
    def validate_reserved_quantity(self):
        if self.quantity_reserved > self.quantity_on_hand:
            raise ValueError("Reserved quantity cannot exceed available stock")
        return self


class InventoryUpdate(BaseModel):
    quantity_on_hand: int | None = Field(
        default=None,
        ge=0,
    )

    quantity_reserved: int | None = Field(
        default=None,
        ge=0,
    )

    reorder_level: int | None = Field(
        default=None,
        ge=0,
    )


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    warehouse_code: str
    quantity_on_hand: int
    quantity_reserved: int
    reorder_level: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
