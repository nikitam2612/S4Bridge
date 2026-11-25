from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.postgres import Base


class Inventory(Base):
    __tablename__ = "inventory"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "warehouse_code",
            name="uq_inventory_product_warehouse",
        ),
        CheckConstraint(
            "quantity_on_hand >= 0",
            name="ck_inventory_quantity_nonnegative",
        ),
        CheckConstraint(
            "quantity_reserved >= 0",
            name="ck_inventory_reserved_nonnegative",
        ),
        CheckConstraint(
            "quantity_reserved <= quantity_on_hand",
            name="ck_inventory_reserved_not_exceed_stock",
        ),
        CheckConstraint(
            "reorder_level >= 0",
            name="ck_inventory_reorder_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    warehouse_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    quantity_on_hand: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    quantity_reserved: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    reorder_level: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
