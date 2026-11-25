from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.schemas.sales_order import SalesOrderCreate


def create_sales_order(
    db: Session,
    order_data: SalesOrderCreate,
) -> SalesOrder:

    try:
        # 1. Validate customer
        customer = db.get(
            Customer,
            order_data.customer_id,
        )

        if customer is None:
            raise ValueError("Customer does not exist")

        if customer.status != "active":
            raise ValueError("Customer is not active")

        # 2. Validate order items
        product_ids = [item.product_id for item in order_data.items]

        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Duplicate products are not allowed in one order")

        products = db.scalars(select(Product).where(Product.id.in_(product_ids))).all()

        product_map = {product.id: product for product in products}

        if len(product_map) != len(product_ids):
            raise ValueError("One or more products do not exist")

        # 3. Validate product status
        for product in products:
            if not product.is_active:
                raise ValueError(f"Product {product.sku} is inactive")

        # 4. Check currency consistency
        currencies = {product.currency for product in products}

        if len(currencies) != 1:
            raise ValueError("All products in an order must use the same currency")

        # 5. Lock inventory records for this warehouse
        inventories = db.scalars(
            select(Inventory)
            .where(
                Inventory.product_id.in_(product_ids),
                Inventory.warehouse_code == order_data.warehouse_code,
            )
            .with_for_update()
        ).all()

        inventory_map = {inventory.product_id: inventory for inventory in inventories}

        # 6. Validate available stock
        for item in order_data.items:
            inventory = inventory_map.get(item.product_id)

            if inventory is None:
                raise ValueError(
                    f"Inventory not found for product "
                    f"{item.product_id} in warehouse "
                    f"{order_data.warehouse_code}"
                )

            available_stock = inventory.quantity_on_hand - inventory.quantity_reserved

            if available_stock < item.quantity:
                raise ValueError(
                    f"Insufficient stock for product "
                    f"{item.product_id}. "
                    f"Available: {available_stock}, "
                    f"Requested: {item.quantity}"
                )

        # 7. Calculate order total
        total_amount = Decimal("0.00")

        order = SalesOrder(
            order_number=f"SO-{uuid4().hex[:12].upper()}",
            customer_id=customer.id,
            warehouse_code=order_data.warehouse_code,
            status="pending",
            total_amount=Decimal("0.00"),
            currency=next(iter(currencies)),
        )

        db.add(order)
        db.flush()

        # 8. Create order items and reserve inventory
        for item in order_data.items:
            product = product_map[item.product_id]
            inventory = inventory_map[item.product_id]

            unit_price = Decimal(str(product.unit_price))

            line_total = unit_price * item.quantity

            total_amount += line_total

            inventory.quantity_reserved += item.quantity

            order.items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )

        # 9. Save final order amount
        order.total_amount = total_amount

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise


def get_sales_order(
    db: Session,
    order_id: int,
) -> SalesOrder | None:

    return db.get(SalesOrder, order_id)


def get_sales_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[SalesOrder]:

    statement = (
        select(SalesOrder).order_by(SalesOrder.id.desc()).offset(skip).limit(limit)
    )

    return list(db.scalars(statement).all())
