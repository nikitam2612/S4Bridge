from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate


def create_inventory(
    db: Session,
    inventory_data: InventoryCreate,
) -> Inventory:

    product = db.get(Product, inventory_data.product_id)

    if product is None:
        raise ValueError("Product does not exist")

    existing_inventory = db.scalar(
        select(Inventory).where(
            Inventory.product_id == inventory_data.product_id,
            Inventory.warehouse_code == inventory_data.warehouse_code,
        )
    )

    if existing_inventory:
        raise ValueError("Inventory already exists for this product and warehouse")

    inventory = Inventory(**inventory_data.model_dump())

    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    return inventory


def get_inventory(
    db: Session,
    inventory_id: int,
) -> Inventory | None:

    return db.get(Inventory, inventory_id)


def get_inventory_by_product(
    db: Session,
    product_id: int,
    warehouse_code: str | None = None,
) -> list[Inventory]:

    statement = select(Inventory).where(Inventory.product_id == product_id)

    if warehouse_code:
        statement = statement.where(Inventory.warehouse_code == warehouse_code)

    statement = statement.order_by(Inventory.warehouse_code)

    return list(db.scalars(statement).all())


def get_all_inventory(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Inventory]:

    statement = select(Inventory).order_by(Inventory.id).offset(skip).limit(limit)

    return list(db.scalars(statement).all())


def update_inventory(
    db: Session,
    inventory_id: int,
    inventory_data: InventoryUpdate,
) -> Inventory | None:

    inventory = db.get(Inventory, inventory_id)

    if inventory is None:
        return None

    update_data = inventory_data.model_dump(exclude_unset=True)

    new_quantity_on_hand = update_data.get(
        "quantity_on_hand",
        inventory.quantity_on_hand,
    )

    new_quantity_reserved = update_data.get(
        "quantity_reserved",
        inventory.quantity_reserved,
    )

    if new_quantity_reserved > new_quantity_on_hand:
        raise ValueError("Reserved quantity cannot exceed quantity on hand")

    for field, value in update_data.items():
        setattr(inventory, field, value)

    db.commit()
    db.refresh(inventory)

    return inventory
